"""
Assessment package for IELTS CLI application.
"""

from .criteria import (
    TaskType,
    AssessmentCriterion,
    BandDescriptor,
    IELTSCriteria,
    CriteriaValidator
)

from .analyzer import (
    ResponseAnalyzer,
    AnalysisError
)

from .scorer import (
    BandCalculator,
    ScoreValidator,
    ScoreComparator,
    ScoreRoundingMethod,
    calculate_band_score,
    validate_and_correct_assessment
)

__all__ = [
    # Criteria
    "TaskType",
    "AssessmentCriterion",
    "BandDescriptor",
    "IELTSCriteria",
    "CriteriaValidator",
    
    # Analyzer
    "ResponseAnalyzer",
    "AnalysisError",
    
    # Scorer
    "BandCalculator",
    "ScoreValidator",
    "ScoreComparator",
    "ScoreRoundingMethod",
    "calculate_band_score",
    "validate_and_correct_assessment"
]
