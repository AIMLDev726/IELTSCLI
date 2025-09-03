"""
Database models for IELTS CLI application using SQLAlchemy.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
import json

Base = declarative_base()


class SessionModel(Base):
    """Database model for practice sessions."""
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Session metadata
    status = Column(String(20), nullable=False, default="not_started")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Task information
    task_type = Column(String(50), nullable=False)
    task_prompt = Column(Text, nullable=False)
    time_limit = Column(Integer, nullable=True)  # in minutes
    word_count_min = Column(Integer, nullable=True)
    word_count_max = Column(Integer, nullable=True)
    task_instructions = Column(JSON, nullable=True)
    
    # User response
    user_response_text = Column(Text, nullable=True)
    user_word_count = Column(Integer, nullable=False, default=0)
    time_taken = Column(Integer, nullable=True)  # in seconds
    submitted_at = Column(DateTime, nullable=True)
    
    # Assessment results (if completed)
    overall_score = Column(Float, nullable=True)
    task_achievement_score = Column(Float, nullable=True)
    coherence_cohesion_score = Column(Float, nullable=True)
    lexical_resource_score = Column(Float, nullable=True)
    grammatical_range_score = Column(Float, nullable=True)
    
    # Feedback
    general_feedback = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    assessor_model = Column(String(100), nullable=True)
    
    # Relationships
    criteria_assessments = relationship("CriteriaAssessmentModel", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_sessions_created_at', 'created_at'),
        Index('idx_sessions_task_type', 'task_type'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_overall_score', 'overall_score'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['not_started', 'in_progress', 'completed', 'cancelled', 'error']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        return status
    
    @validates('task_type')
    def validate_task_type(self, key, task_type):
        valid_types = [
            'writing_task_1_academic', 'writing_task_1_general', 'writing_task_2',
            'speaking_part_1', 'speaking_part_2', 'speaking_part_3',
            'reading_academic', 'reading_general', 'listening'
        ]
        if task_type not in valid_types:
            raise ValueError(f"Invalid task type: {task_type}")
        return task_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'task_type': self.task_type,
            'task_prompt': self.task_prompt,
            'time_limit': self.time_limit,
            'word_count_min': self.word_count_min,
            'word_count_max': self.word_count_max,
            'task_instructions': self.task_instructions,
            'user_response_text': self.user_response_text,
            'user_word_count': self.user_word_count,
            'time_taken': self.time_taken,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'overall_score': self.overall_score,
            'task_achievement_score': self.task_achievement_score,
            'coherence_cohesion_score': self.coherence_cohesion_score,
            'lexical_resource_score': self.lexical_resource_score,
            'grammatical_range_score': self.grammatical_range_score,
            'general_feedback': self.general_feedback,
            'recommendations': self.recommendations,
            'assessor_model': self.assessor_model
        }


class CriteriaAssessmentModel(Base):
    """Database model for individual criteria assessments."""
    
    __tablename__ = "criteria_assessments"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to session
    session_id = Column(String(36), ForeignKey('sessions.session_id', ondelete='CASCADE'), nullable=False)
    
    # Criteria information
    criterion_name = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=True)
    areas_for_improvement = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("SessionModel", back_populates="criteria_assessments")
    
    # Constraints and indexes
    __table_args__ = (
        Index('idx_criteria_session_id', 'session_id'),
        Index('idx_criteria_name', 'criterion_name'),
        Index('idx_criteria_score', 'score'),
        UniqueConstraint('session_id', 'criterion_name', name='uq_session_criterion'),
    )
    
    @validates('score')
    def validate_score(self, key, score):
        if score < 0 or score > 9:
            raise ValueError(f"Score must be between 0 and 9: {score}")
        # Check if score is in 0.5 increments
        if (score * 2) % 1 != 0:
            raise ValueError(f"Score must be in 0.5 increments: {score}")
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'criterion_name': self.criterion_name,
            'score': self.score,
            'feedback': self.feedback,
            'strengths': self.strengths,
            'areas_for_improvement': self.areas_for_improvement
        }


class UserStatsModel(Base):
    """Database model for user statistics and progress tracking."""
    
    __tablename__ = "user_stats"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Statistics metadata
    stats_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_sessions = Column(Integer, nullable=False, default=0)
    completed_sessions = Column(Integer, nullable=False, default=0)
    
    # Performance metrics
    average_score = Column(Float, nullable=True)
    best_score = Column(Float, nullable=True)
    improvement_trend = Column(Float, nullable=True)
    
    # Task type distribution
    writing_task_2_count = Column(Integer, nullable=False, default=0)
    writing_task_1_count = Column(Integer, nullable=False, default=0)
    speaking_count = Column(Integer, nullable=False, default=0)
    reading_count = Column(Integer, nullable=False, default=0)
    listening_count = Column(Integer, nullable=False, default=0)
    
    # Time tracking
    total_practice_time = Column(Integer, nullable=False, default=0)  # in seconds
    average_session_time = Column(Integer, nullable=True)  # in seconds
    
    # Indexes
    __table_args__ = (
        Index('idx_user_stats_date', 'stats_date'),
        Index('idx_user_stats_best_score', 'best_score'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'stats_date': self.stats_date.isoformat() if self.stats_date else None,
            'total_sessions': self.total_sessions,
            'completed_sessions': self.completed_sessions,
            'average_score': self.average_score,
            'best_score': self.best_score,
            'improvement_trend': self.improvement_trend,
            'writing_task_2_count': self.writing_task_2_count,
            'writing_task_1_count': self.writing_task_1_count,
            'speaking_count': self.speaking_count,
            'reading_count': self.reading_count,
            'listening_count': self.listening_count,
            'total_practice_time': self.total_practice_time,
            'average_session_time': self.average_session_time
        }


class ErrorLogModel(Base):
    """Database model for error logging and debugging."""
    
    __tablename__ = "error_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    error_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Error information
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    error_context = Column(JSON, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_action = Column(String(200), nullable=True)
    resolved = Column(Boolean, nullable=False, default=False)
    
    # Related session (if applicable)
    session_id = Column(String(36), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_error_logs_timestamp', 'timestamp'),
        Index('idx_error_logs_type', 'error_type'),
        Index('idx_error_logs_resolved', 'resolved'),
        Index('idx_error_logs_session_id', 'session_id'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'error_id': self.error_id,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'error_context': self.error_context,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_action': self.user_action,
            'resolved': self.resolved,
            'session_id': self.session_id
        }


class ConfigBackupModel(Base):
    """Database model for configuration backups."""
    
    __tablename__ = "config_backups"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    backup_id = Column(String(36), unique=True, nullable=False, index=True)
    
    # Backup information
    config_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    backup_type = Column(String(50), nullable=False, default="manual")  # manual, automatic, migration
    description = Column(String(500), nullable=True)
    
    # Metadata
    app_version = Column(String(20), nullable=True)
    user_initiated = Column(Boolean, nullable=False, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_config_backups_created_at', 'created_at'),
        Index('idx_config_backups_type', 'backup_type'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'backup_id': self.backup_id,
            'config_data': self.config_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'backup_type': self.backup_type,
            'description': self.description,
            'app_version': self.app_version,
            'user_initiated': self.user_initiated
        }


# Utility functions for model conversions
def session_model_to_practice_session(session_model: SessionModel) -> Optional[Any]:
    """
    Convert SessionModel to PracticeSession domain object.
    
    Args:
        session_model: Database model instance
        
    Returns:
        PracticeSession domain object or None if conversion fails
    """
    try:
        from ..core.models import (
            PracticeSession, TaskPrompt, UserResponse, 
            Assessment, AssessmentCriteria, BandScore, TaskType
        )
        
        # Create TaskPrompt
        task_prompt = TaskPrompt(
            task_type=TaskType(session_model.task_type),
            prompt_text=session_model.task_prompt,
            time_limit=session_model.time_limit,
            word_count_min=session_model.word_count_min,
            word_count_max=session_model.word_count_max,
            instructions=session_model.task_instructions or []
        )
        
        # Create UserResponse
        user_response = UserResponse(
            text=session_model.user_response_text or "",
            word_count=session_model.user_word_count,
            time_taken=session_model.time_taken,
            submitted_at=session_model.submitted_at or datetime.now()
        )
        
        # Create Assessment if available
        assessment = None
        if session_model.overall_score is not None:
            # Create criteria assessments from individual score fields
            criteria_scores = []
            
            # Build criteria from the individual score fields in the sessions table
            criteria_names = [
                ("Task Achievement", session_model.task_achievement_score),
                ("Coherence and Cohesion", session_model.coherence_cohesion_score),
                ("Lexical Resource", session_model.lexical_resource_score),
                ("Grammatical Range and Accuracy", session_model.grammatical_range_score)
            ]
            
            for criterion_name, score in criteria_names:
                if score is not None:
                    criteria = AssessmentCriteria(
                        criterion_name=criterion_name,
                        score=score,
                        feedback="",  # Individual feedback not stored in old schema
                        strengths=[],
                        areas_for_improvement=[]
                    )
                    criteria_scores.append(criteria)
            
            assessment = Assessment(
                overall_band_score=session_model.overall_score,
                criteria_scores=criteria_scores,
                overall_feedback=session_model.general_feedback or "",
                recommendations=session_model.recommendations or [],
                assessor_model=session_model.assessor_model or "unknown"
            )
        
        # Create PracticeSession
        practice_session = PracticeSession(
            session_id=session_model.session_id,
            task_prompt=task_prompt,
            user_response=user_response,
            assessment=assessment,
            status=session_model.status,
            created_at=session_model.created_at,
            started_at=session_model.created_at,  # Use created_at as started_at for existing data
            completed_at=session_model.completed_at
        )
        
        return practice_session
        
    except Exception as e:
        print(f"Error converting session model: {e}")
        return None


def practice_session_to_session_model(practice_session: Any) -> SessionModel:
    """
    Convert PracticeSession domain object to SessionModel.
    
    Args:
        practice_session: Domain object
        
    Returns:
        Database model instance
    """
    session_model = SessionModel(
        session_id=practice_session.session_id,
        status=practice_session.status,
        created_at=practice_session.created_at,
        completed_at=practice_session.completed_at,
        
        # Task information
        task_type=practice_session.task_prompt.task_type.value,
        task_prompt=practice_session.task_prompt.prompt_text,
        time_limit=practice_session.task_prompt.time_limit,
        word_count_min=practice_session.task_prompt.word_count_min,
        word_count_max=practice_session.task_prompt.word_count_max,
        task_instructions=practice_session.task_prompt.instructions,
        
        # User response
        user_response_text=practice_session.user_response.text,
        user_word_count=practice_session.user_response.word_count,
        time_taken=practice_session.user_response.time_taken,
        submitted_at=practice_session.user_response.submitted_at
    )
    
    # Add assessment data if available
    if practice_session.assessment:
        session_model.overall_score = practice_session.assessment.overall_band_score
        session_model.general_feedback = practice_session.assessment.overall_feedback
        session_model.recommendations = practice_session.assessment.recommendations
        session_model.assessor_model = practice_session.assessment.assessor_model
    
    return session_model
