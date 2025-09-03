"""
Practice session management for IELTS CLI application.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from ..core.models import (
    PracticeSession, 
    TaskPrompt, 
    UserResponse, 
    Assessment,
    TaskType,
    SessionStats
)
from ..assessment import AnalysisError, ResponseAnalyzer
from ..llm.client import LLMClient, LLMError
from ..storage.database import session_manager
from ..utils import display_error, display_success, display_info, format_duration


class SessionStatus(str, Enum):
    """Practice session status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AWAITING_SUBMISSION = "awaiting_submission"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class SessionError(Exception):
    """Exception raised for session-related errors."""
    pass


class SessionManager:
    """Manages IELTS practice sessions from start to completion."""
    
    def __init__(self, llm_client: LLMClient = None):
        """
        Initialize the session manager.
        
        Args:
            llm_client: LLM client for assessment (optional, can be set later)
        """
        self.current_session: Optional[PracticeSession] = None
        self.session_start_time: Optional[datetime] = None
        self.user_input_buffer: str = ""
        self.auto_save_interval: int = 30  # seconds
        self._auto_save_task: Optional[asyncio.Task] = None
        self.llm_client = llm_client
        self.analyzer = ResponseAnalyzer(llm_client) if llm_client else None
    
    async def create_session(
        self, 
        task_type: TaskType = TaskType.WRITING_TASK_2,
        custom_prompt: str = None,
        time_limit: int = None
    ) -> PracticeSession:
        """
        Create a new practice session.
        
        Args:
            task_type: Type of IELTS task
            custom_prompt: Custom task prompt (if None, generates one)
            time_limit: Time limit in minutes (if None, uses default)
            
        Returns:
            Created practice session
            
        Raises:
            SessionError: If session creation fails
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create or generate task prompt
            if custom_prompt:
                task_prompt = TaskPrompt(
                    task_type=task_type,
                    prompt_text=custom_prompt,
                    time_limit=time_limit or self._get_default_time_limit(task_type),
                    word_count_min=self._get_word_count_requirements(task_type)[0],
                    word_count_max=self._get_word_count_requirements(task_type)[1]
                )
            else:
                task_prompt = await self._generate_task_prompt(task_type, time_limit)
            
            # Create initial user response
            user_response = UserResponse(
                text="[Response not submitted yet]",
                word_count=0,
                time_taken=0
            )
            
            # Create session
            session = PracticeSession(
                session_id=session_id,
                task_prompt=task_prompt,
                user_response=user_response,
                status=SessionStatus.NOT_STARTED.value
            )
            
            # Save to database
            await session_manager.save_session(session)
            
            self.current_session = session
            display_success(f"Practice session created (ID: {session_id[:8]})")
            
            return session
            
        except Exception as e:
            raise SessionError(f"Failed to create session: {e}")
    
    async def start_session(self, session: PracticeSession = None) -> None:
        """
        Start a practice session.
        
        Args:
            session: Session to start (if None, uses current session)
            
        Raises:
            SessionError: If session start fails
        """
        try:
            if session is None:
                session = self.current_session
            
            if not session:
                raise SessionError("No session to start")
            
            # Update session status
            session.status = SessionStatus.IN_PROGRESS.value
            self.current_session = session
            self.session_start_time = datetime.now()
            
            # Start auto-save
            await self._start_auto_save()
            
            # Save to database
            await session_manager.save_session(session)
            
            display_info("Practice session started. Begin writing your response.")
            display_info(f"Time limit: {session.task_prompt.time_limit} minutes")
            display_info(f"Word count requirement: {session.task_prompt.word_count_min}+ words")
            
        except Exception as e:
            raise SessionError(f"Failed to start session: {e}")
    
    def update_user_input(self, text: str) -> None:
        """
        Update user input in the current session.
        
        Args:
            text: Updated user response text
        """
        if not self.current_session:
            return
        
        self.user_input_buffer = text
        word_count = len(text.split()) if text else 0
        
        # Update user response
        self.current_session.user_response.text = text
        self.current_session.user_response.word_count = word_count
        
        # Update time taken
        if self.session_start_time:
            time_taken = (datetime.now() - self.session_start_time).total_seconds()
            self.current_session.user_response.time_taken = int(time_taken)
    
    async def submit_response(self, session: PracticeSession = None) -> Assessment:
        """
        Submit user response for assessment.
        
        Args:
            session: Session to submit (if None, uses current session)
            
        Returns:
            Assessment result
            
        Raises:
            SessionError: If submission fails
        """
        try:
            if session is None:
                session = self.current_session
            
            if not session:
                raise SessionError("No session to submit")
            
            if not session.user_response.text.strip():
                raise SessionError("Cannot submit empty response")
            
            # Check minimum word count
            word_count = session.user_response.word_count
            min_words = session.task_prompt.word_count_min
            
            if word_count < min_words:
                display_error(
                    f"Response too short: {word_count} words (minimum: {min_words}). "
                    f"Submit anyway? This will affect your score."
                )
            
            # Update session status
            session.status = SessionStatus.PROCESSING.value
            
            # Stop auto-save
            await self._stop_auto_save()
            
            # Update final timing
            if self.session_start_time:
                final_time = (datetime.now() - self.session_start_time).total_seconds()
                session.user_response.time_taken = int(final_time)
            
            session.user_response.submitted_at = datetime.now()
            
            display_info("Processing your response... This may take a moment.")
            
            # Check if analyzer is available
            if not self.analyzer:
                raise SessionError("No analyzer available. Please ensure LLM client is configured.")
            
            # Analyze response
            assessment = await self.analyzer.analyze_response(
                task_prompt=session.task_prompt.prompt_text,
                user_response=session.user_response,
                task_type=session.task_prompt.task_type.value
            )
            
            # Complete session
            session.complete_session(assessment)
            
            # Save to database
            await session_manager.save_session(session)
            
            display_success("Response submitted and assessed!")
            
            return assessment
            
        except AnalysisError as e:
            session.status = SessionStatus.ERROR.value
            await session_manager.save_session(session)
            raise SessionError(f"Assessment failed: {e}")
        except Exception as e:
            if session:
                session.status = SessionStatus.ERROR.value
                await session_manager.save_session(session)
            raise SessionError(f"Failed to submit response: {e}")
    
    async def cancel_session(self, session: PracticeSession = None) -> None:
        """
        Cancel a practice session.
        
        Args:
            session: Session to cancel (if None, uses current session)
            
        Raises:
            SessionError: If cancellation fails
        """
        try:
            if session is None:
                session = self.current_session
            
            if not session:
                return
            
            # Stop auto-save
            await self._stop_auto_save()
            
            # Cancel session
            session.cancel_session()
            
            # Save to database
            await session_manager.save_session(session)
            
            # Clear current session
            if session == self.current_session:
                self.current_session = None
                self.session_start_time = None
                self.user_input_buffer = ""
            
            display_info("Practice session cancelled")
            
        except Exception as e:
            raise SessionError(f"Failed to cancel session: {e}")
    
    async def pause_session(self) -> None:
        """Pause the current session."""
        if self.current_session and self.current_session.status == SessionStatus.IN_PROGRESS.value:
            await self._stop_auto_save()
            display_info("Session paused. Use 'resume' to continue.")
    
    async def resume_session(self) -> None:
        """Resume the current session."""
        if self.current_session:
            await self._start_auto_save()
            display_info("Session resumed.")
    
    async def get_session_stats(self, session_id: str = None) -> Dict[str, Any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session ID (if None, uses current session)
            
        Returns:
            Dictionary with session statistics
        """
        try:
            if session_id:
                session = await session_manager.get_session(session_id)
            else:
                session = self.current_session
            
            if not session:
                return {}
            
            stats = {
                "session_id": session.session_id,
                "task_type": session.task_prompt.task_type.value,
                "status": session.status,
                "word_count": session.user_response.word_count,
                "time_taken": format_duration(session.user_response.time_taken or 0),
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
            
            if session.assessment:
                stats["overall_score"] = session.assessment.overall_band_score
                stats["criteria_scores"] = {
                    criterion.criterion_name: criterion.score 
                    for criterion in session.assessment.criteria_scores
                }
            
            return stats
            
        except Exception as e:
            raise SessionError(f"Failed to get session stats: {e}")
    
    async def list_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent practice sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        try:
            sessions = await session_manager.get_recent_sessions(limit)
            
            session_list = []
            for session in sessions:
                summary = {
                    "session_id": session.session_id[:8],  # Short ID for display
                    "task_type": session.task_prompt.task_type.value,
                    "status": session.status,
                    "word_count": session.user_response.word_count,
                    "created_at": session.created_at.strftime("%Y-%m-%d %H:%M"),
                    "overall_score": None
                }
                
                if session.assessment:
                    summary["overall_score"] = session.assessment.overall_band_score
                
                session_list.append(summary)
            
            return session_list
            
        except Exception as e:
            raise SessionError(f"Failed to list sessions: {e}")
    
    async def _generate_task_prompt(
        self, 
        task_type: TaskType, 
        time_limit: int = None
    ) -> TaskPrompt:
        """Generate a task prompt using LLM."""
        try:
            if not self.llm_client:
                raise SessionError("No LLM client available for prompt generation.")
            
            # Determine difficulty level based on recent performance
            difficulty = "medium"  # Default
            
            if task_type == TaskType.WRITING_TASK_2:
                prompt_text = await self.llm_client.generate_writing_prompt(difficulty)
            else:
                raise SessionError(f"Prompt generation not implemented for {task_type}")
            
            return TaskPrompt(
                task_type=task_type,
                prompt_text=prompt_text,
                time_limit=time_limit or self._get_default_time_limit(task_type),
                word_count_min=self._get_word_count_requirements(task_type)[0],
                word_count_max=self._get_word_count_requirements(task_type)[1]
            )
            
        except LLMError as e:
            raise SessionError(f"Failed to generate prompt: {e}")
    
    def _get_default_time_limit(self, task_type: TaskType) -> int:
        """Get default time limit for task type."""
        if task_type == TaskType.WRITING_TASK_2:
            return 40
        elif task_type in [TaskType.WRITING_TASK_1_ACADEMIC, TaskType.WRITING_TASK_1_GENERAL]:
            return 20
        else:
            return 30
    
    def _get_word_count_requirements(self, task_type: TaskType) -> tuple:
        """Get word count requirements for task type."""
        if task_type == TaskType.WRITING_TASK_2:
            return (250, 350)
        elif task_type in [TaskType.WRITING_TASK_1_ACADEMIC, TaskType.WRITING_TASK_1_GENERAL]:
            return (150, 200)
        else:
            return (200, 300)
    
    async def _start_auto_save(self) -> None:
        """Start auto-save task."""
        if self._auto_save_task:
            return
        
        self._auto_save_task = asyncio.create_task(self._auto_save_loop())
    
    async def _stop_auto_save(self) -> None:
        """Stop auto-save task."""
        if self._auto_save_task:
            self._auto_save_task.cancel()
            try:
                await self._auto_save_task
            except asyncio.CancelledError:
                pass
            self._auto_save_task = None
    
    async def _auto_save_loop(self) -> None:
        """Auto-save loop that runs in the background."""
        try:
            while True:
                await asyncio.sleep(self.auto_save_interval)
                
                if self.current_session and self.user_input_buffer:
                    try:
                        # Update current text
                        self.update_user_input(self.user_input_buffer)
                        
                        # Save to database
                        await session_manager.save_session(self.current_session)
                        
                    except Exception as e:
                        # Don't interrupt the session for auto-save errors
                        print(f"Auto-save failed: {e}")
                        
        except asyncio.CancelledError:
            # Task was cancelled, which is expected
            pass
    
    def get_current_session(self) -> Optional[PracticeSession]:
        """Get the current active session."""
        return self.current_session
    
    def is_session_active(self) -> bool:
        """Check if there's an active session."""
        return (
            self.current_session is not None and 
            self.current_session.status in [
                SessionStatus.IN_PROGRESS.value,
                SessionStatus.AWAITING_SUBMISSION.value
            ]
        )
    
    def get_session_time_remaining(self) -> Optional[int]:
        """
        Get remaining time for current session in seconds.
        
        Returns:
            Remaining time in seconds, or None if no active session
        """
        if not self.is_session_active() or not self.session_start_time:
            return None
        
        elapsed = (datetime.now() - self.session_start_time).total_seconds()
        time_limit = self.current_session.task_prompt.time_limit * 60  # Convert to seconds
        
        remaining = time_limit - elapsed
        return max(0, int(remaining))
    
    async def get_user_statistics(self) -> SessionStats:
        """
        Get comprehensive user statistics.
        
        Returns:
            SessionStats object with user performance data
        """
        try:
            # Get all user sessions
            all_sessions = await session_manager.get_all_user_sessions()
            
            # Create and update statistics
            stats = SessionStats()
            stats.update_stats(all_sessions)
            
            return stats
            
        except Exception as e:
            raise SessionError(f"Failed to get user statistics: {e}")


# Note: Global session manager instance removed due to LLM client requirement
# Create SessionManager instances with proper LLM client as needed
