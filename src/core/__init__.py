"""
Core package for IELTS CLI application.
"""

from .models import (
    TaskType,
    LLMProvider,
    BandScore,
    ModelConfig,
    UserPreferences,
    AppConfig,
    TaskPrompt,
    UserResponse,
    AssessmentCriteria,
    Assessment,
    PracticeSession,
    SessionStats,
    ErrorLog
)

from .config import (
    ConfigManager,
    SecureStorage,
    ConfigurationError,
    config_manager
)

# Note: Session imports removed to avoid circular dependencies
# Import SessionManager directly from .session when needed

__all__ = [
    # Models
    "TaskType",
    "LLMProvider",
    "BandScore",
    "ModelConfig",
    "UserPreferences",
    "AppConfig",
    "TaskPrompt",
    "UserResponse", 
    "AssessmentCriteria",
    "Assessment",
    "PracticeSession",
    "SessionStats",
    "ErrorLog",
    
    # Config
    "ConfigManager",
    "SecureStorage",
    "ConfigurationError",
    "config_manager"
]
