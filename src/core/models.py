"""
Data models for IELTS CLI application using Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator, model_validator


class TaskType(str, Enum):
    """IELTS task types enumeration."""
    WRITING_TASK_1_ACADEMIC = "writing_task_1_academic"
    WRITING_TASK_1_GENERAL = "writing_task_1_general"
    WRITING_TASK_2 = "writing_task_2"
    SPEAKING_PART_1 = "speaking_part_1"
    SPEAKING_PART_2 = "speaking_part_2"
    SPEAKING_PART_3 = "speaking_part_3"
    READING_ACADEMIC = "reading_academic"
    READING_GENERAL = "reading_general"
    LISTENING = "listening"


class LLMProvider(str, Enum):
    """LLM provider enumeration."""
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"


class BandScore(BaseModel):
    """IELTS band score model."""
    overall: float = Field(..., ge=0, le=9, description="Overall band score")
    task_achievement: Optional[float] = Field(None, ge=0, le=9, description="Task Achievement score")
    coherence_cohesion: Optional[float] = Field(None, ge=0, le=9, description="Coherence and Cohesion score")
    lexical_resource: Optional[float] = Field(None, ge=0, le=9, description="Lexical Resource score")
    grammatical_range: Optional[float] = Field(None, ge=0, le=9, description="Grammatical Range and Accuracy score")
    
    @validator('overall', 'task_achievement', 'coherence_cohesion', 'lexical_resource', 'grammatical_range')
    def validate_band_scores(cls, v):
        """Validate that scores are in 0.5 increments."""
        if v is not None and (v * 2) % 1 != 0:
            raise ValueError("Band scores must be in 0.5 increments")
        return v


class ModelConfig(BaseModel):
    """Model configuration for LLM providers."""
    model: str = Field(..., min_length=1, description="Model name")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL for the provider")
    temperature: float = Field(0.7, ge=0, le=2, description="Temperature for text generation")
    is_custom_model: bool = Field(False, description="Whether this is a custom model")
    
    @validator('api_key')
    def validate_api_key(cls, v, values):
        """Validate API key based on provider requirements."""
        # This validation will be handled by the InputValidator in utils
        return v


class UserPreferences(BaseModel):
    """User preferences model."""
    default_task_type: TaskType = Field(TaskType.WRITING_TASK_2, description="Default task type")
    show_detailed_feedback: bool = Field(True, description="Show detailed feedback")
    save_sessions: bool = Field(True, description="Save practice sessions")
    auto_submit_timeout: Optional[int] = Field(None, ge=30, description="Auto-submit timeout in seconds")
    feedback_language: str = Field("en", description="Language for feedback")
    word_count_warnings: bool = Field(True, description="Show word count warnings")
    
    @validator('feedback_language')
    def validate_language(cls, v):
        """Validate feedback language code."""
        valid_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ko']
        if v not in valid_languages:
            raise ValueError(f"Language must be one of: {', '.join(valid_languages)}")
        return v


class AppConfig(BaseModel):
    """Main application configuration model."""
    llm_provider: LLMProvider = Field(LLMProvider.OPENAI, description="Current LLM provider")
    model_configs: Dict[LLMProvider, ModelConfig] = Field(..., description="Model configurations for each provider")
    user_preferences: UserPreferences = Field(default_factory=UserPreferences, description="User preferences")
    default_task_type: TaskType = Field(TaskType.WRITING_TASK_2, description="Default task type for practice sessions")
    version: str = Field("1.0.0", description="Configuration version")
    created_at: datetime = Field(default_factory=datetime.now, description="Configuration creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @model_validator(mode='after')
    def validate_current_provider_config(self):
        """Validate that the current provider has a valid configuration."""
        if self.llm_provider not in self.model_configs:
            raise ValueError(f"No configuration found for provider: {self.llm_provider}")
        
        return self
    
    def get_current_model_config(self) -> ModelConfig:
        """Get the model configuration for the current provider."""
        return self.model_configs[self.llm_provider]
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()


class TaskPrompt(BaseModel):
    """IELTS task prompt model."""
    task_type: TaskType = Field(..., description="Type of IELTS task")
    prompt_text: str = Field(..., min_length=10, description="The task prompt text")
    time_limit: Optional[int] = Field(None, ge=1, description="Time limit in minutes")
    word_count_min: Optional[int] = Field(None, ge=1, description="Minimum word count")
    word_count_max: Optional[int] = Field(None, ge=1, description="Maximum word count")
    instructions: List[str] = Field(default_factory=list, description="Additional instructions")
    
    @model_validator(mode='after')
    def validate_word_counts(self):
        """Validate that max word count is greater than min word count."""
        if self.word_count_max and self.word_count_min and self.word_count_max <= self.word_count_min:
            raise ValueError("Maximum word count must be greater than minimum word count")
        
        return self


class UserResponse(BaseModel):
    """User response to an IELTS task."""
    text: str = Field(..., min_length=1, description="User's response text")
    word_count: int = Field(..., ge=0, description="Word count of the response")
    time_taken: Optional[int] = Field(None, ge=0, description="Time taken in seconds")
    submitted_at: datetime = Field(default_factory=datetime.now, description="Submission timestamp")
    
    @validator('word_count', always=True)
    def calculate_word_count(cls, v, values):
        """Calculate word count from text if not provided."""
        text = values.get('text', '')
        if not v:
            return len(text.split())
        return v


class AssessmentCriteria(BaseModel):
    """Assessment criteria for IELTS evaluation."""
    criterion_name: str = Field(..., description="Name of the assessment criterion")
    score: float = Field(..., ge=0, le=9, description="Score for this criterion")
    feedback: str = Field(..., description="Detailed feedback for this criterion")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    
    @validator('score')
    def validate_score_increment(cls, v):
        """Validate that score is in 0.5 increments."""
        if (v * 2) % 1 != 0:
            raise ValueError("Score must be in 0.5 increments")
        return v


class Assessment(BaseModel):
    """Complete IELTS assessment result."""
    overall_band_score: float = Field(..., ge=0, le=9, description="Overall band score")
    criteria_scores: List[AssessmentCriteria] = Field(..., description="Individual criteria assessments")
    overall_feedback: str = Field(..., description="Overall feedback on the response")
    detailed_feedback: Optional[Dict[str, List[str]]] = Field(None, description="Detailed feedback sections")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    assessed_at: datetime = Field(default_factory=datetime.now, description="Assessment timestamp")
    assessor_model: str = Field(..., description="Model used for assessment")
    
    @validator('overall_band_score')
    def validate_band_score(cls, v):
        """Validate that band score is in 0.5 increments."""
        if (v * 2) % 1 != 0:
            raise ValueError("Band score must be in 0.5 increments")
        return v
    
    def get_criterion_score(self, criterion_name: str) -> Optional[AssessmentCriteria]:
        """Get score for a specific criterion."""
        for criteria in self.criteria_scores:
            if criteria.criterion_name.lower() == criterion_name.lower():
                return criteria
        return None


class PracticeSession(BaseModel):
    """Complete practice session model."""
    session_id: str = Field(..., description="Unique session identifier")
    task_prompt: TaskPrompt = Field(..., description="The task prompt")
    user_response: UserResponse = Field(..., description="User's response")
    assessment: Optional[Assessment] = Field(None, description="Assessment result")
    status: str = Field("in_progress", description="Session status")
    quick_mode: bool = Field(False, description="Whether this is a quick practice session")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit in minutes")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Session start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Session completion timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate session status."""
        valid_statuses = ['not_started', 'in_progress', 'completed', 'cancelled', 'error']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v
    
    def start_session(self):
        """Start the session."""
        self.started_at = datetime.now()
        if self.status != "in_progress":
            self.status = "in_progress"
    
    def submit_response(self, response_text: str):
        """Submit user response to the session."""
        word_count = len(response_text.split()) if response_text.strip() else 0
        self.user_response = UserResponse(
            text=response_text,
            word_count=word_count,
            submitted_at=datetime.now()
        )
    
    def set_assessment(self, assessment):
        """Set the assessment for the session."""
        self.assessment = assessment
    
    def complete_session(self, assessment: Optional['Assessment'] = None):
        """Mark session as completed with optional assessment."""
        if assessment:
            self.assessment = assessment
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def cancel_session(self):
        """Cancel the session."""
        self.status = "cancelled"
        self.completed_at = datetime.now()


class SessionStats(BaseModel):
    """Statistics for practice sessions."""
    total_sessions: int = Field(0, ge=0, description="Total number of sessions")
    completed_sessions: int = Field(0, ge=0, description="Number of completed sessions")
    average_score: Optional[float] = Field(None, ge=0, le=9, description="Average overall score")
    best_score: Optional[float] = Field(None, ge=0, le=9, description="Best overall score")
    improvement_trend: Optional[float] = Field(None, description="Improvement trend (positive/negative)")
    task_type_distribution: Dict[TaskType, int] = Field(default_factory=dict, description="Distribution of task types")
    last_session_date: Optional[datetime] = Field(None, description="Date of last session")
    
    def update_stats(self, sessions: List[PracticeSession]):
        """Update statistics based on a list of sessions."""
        self.total_sessions = len(sessions)
        completed = [s for s in sessions if s.status == "completed" and s.assessment and s.assessment.overall_band_score is not None]
        self.completed_sessions = len(completed)
        
        if completed:
            scores = [s.assessment.overall_band_score for s in completed if s.assessment and s.assessment.overall_band_score is not None]
            if scores:  # Only calculate if we have valid scores
                self.average_score = sum(scores) / len(scores)
                self.best_score = max(scores)
                
                # Get last session date from sessions with valid completion dates
                completion_dates = [s.completed_at for s in completed if s.completed_at is not None]
                if completion_dates:
                    self.last_session_date = max(completion_dates)
                
                # Calculate task type distribution
                self.task_type_distribution = {}
                for session in completed:
                    task_type = session.task_prompt.task_type
                    self.task_type_distribution[task_type] = self.task_type_distribution.get(task_type, 0) + 1
                
                # Calculate improvement trend (simple linear regression slope)
                if len(scores) > 1:
                    n = len(scores)
                    sum_x = sum(range(n))
                    sum_y = sum(scores)
                    sum_xy = sum(i * score for i, score in enumerate(scores))
                    sum_x2 = sum(i * i for i in range(n))
                    
                    denominator = n * sum_x2 - sum_x * sum_x
                    if denominator != 0:  # Avoid division by zero
                        self.improvement_trend = (n * sum_xy - sum_x * sum_y) / denominator


class ErrorLog(BaseModel):
    """Error log entry model."""
    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    user_action: Optional[str] = Field(None, description="User action that caused the error")
    resolved: bool = Field(False, description="Whether the error has been resolved")
    
    def mark_resolved(self):
        """Mark the error as resolved."""
        self.resolved = True
