"""
Band score calculation utilities for IELTS assessments.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
import statistics

from ..core.models import BandScore, Assessment, AssessmentCriteria
from .criteria import (
    AssessmentCriterion, 
    CriteriaValidator, 
    IELTSCriteria,
    TaskType
)


class ScoreRoundingMethod(Enum):
    """Methods for rounding IELTS band scores."""
    NEAREST_HALF = "nearest_half"
    CONSERVATIVE = "conservative"  # Round down
    OPTIMISTIC = "optimistic"     # Round up


class BandCalculator:
    """Calculator for IELTS band scores with various rounding methods."""
    
    @staticmethod
    def round_to_band_score(
        score: float, 
        method: ScoreRoundingMethod = ScoreRoundingMethod.NEAREST_HALF
    ) -> float:
        """
        Round a score to valid IELTS band score (0.5 increments).
        
        Args:
            score: Raw score to round
            method: Rounding method to use
            
        Returns:
            Rounded band score
        """
        if score < 0:
            return 0.0
        if score > 9:
            return 9.0
        
        if method == ScoreRoundingMethod.NEAREST_HALF:
            return round(score * 2) / 2
        elif method == ScoreRoundingMethod.CONSERVATIVE:
            return int(score * 2) / 2
        elif method == ScoreRoundingMethod.OPTIMISTIC:
            return (int(score * 2) + 1) / 2
        else:
            return round(score * 2) / 2
    
    @staticmethod
    def calculate_overall_score(
        criterion_scores: Dict[AssessmentCriterion, float],
        weights: Optional[Dict[AssessmentCriterion, float]] = None,
        rounding_method: ScoreRoundingMethod = ScoreRoundingMethod.NEAREST_HALF
    ) -> float:
        """
        Calculate overall band score from individual criterion scores.
        
        Args:
            criterion_scores: Dictionary of criterion scores
            weights: Optional weights for each criterion (default: equal weights)
            rounding_method: Method for rounding the final score
            
        Returns:
            Overall band score
        """
        if not criterion_scores:
            return 0.0
        
        # Validate scores
        if not CriteriaValidator.validate_criterion_scores(criterion_scores):
            raise ValueError("Invalid criterion scores provided")
        
        # Use equal weights if not provided
        if weights is None:
            weights = {criterion: 0.25 for criterion in criterion_scores.keys()}
        
        # Ensure weights sum to 1.0
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            # Normalize weights
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted average
        weighted_sum = sum(
            score * weights.get(criterion, 0.25) 
            for criterion, score in criterion_scores.items()
        )
        
        return BandCalculator.round_to_band_score(weighted_sum, rounding_method)
    
    @staticmethod
    def calculate_detailed_band_score(
        criterion_scores: Dict[AssessmentCriterion, float]
    ) -> BandScore:
        """
        Calculate detailed band scores for all criteria.
        
        Args:
            criterion_scores: Dictionary of criterion scores
            
        Returns:
            BandScore object with all scores
        """
        # Calculate overall score
        overall = BandCalculator.calculate_overall_score(criterion_scores)
        
        # Extract individual scores (rounded to valid band scores)
        task_achievement = None
        coherence_cohesion = None
        lexical_resource = None
        grammatical_range = None
        
        for criterion, score in criterion_scores.items():
            rounded_score = BandCalculator.round_to_band_score(score)
            
            if criterion in [AssessmentCriterion.TASK_ACHIEVEMENT, AssessmentCriterion.TASK_RESPONSE]:
                task_achievement = rounded_score
            elif criterion == AssessmentCriterion.COHERENCE_COHESION:
                coherence_cohesion = rounded_score
            elif criterion == AssessmentCriterion.LEXICAL_RESOURCE:
                lexical_resource = rounded_score
            elif criterion == AssessmentCriterion.GRAMMATICAL_RANGE:
                grammatical_range = rounded_score
        
        return BandScore(
            overall=overall,
            task_achievement=task_achievement,
            coherence_cohesion=coherence_cohesion,
            lexical_resource=lexical_resource,
            grammatical_range=grammatical_range
        )
    
    @staticmethod
    def calculate_score_distribution(scores: List[float]) -> Dict[str, float]:
        """
        Calculate statistical distribution of scores.
        
        Args:
            scores: List of scores
            
        Returns:
            Dictionary with statistical measures
        """
        if not scores:
            return {}
        
        return {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "mode": statistics.mode(scores) if len(set(scores)) < len(scores) else None,
            "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "min": min(scores),
            "max": max(scores),
            "range": max(scores) - min(scores)
        }
    
    @staticmethod
    def analyze_score_consistency(
        assessments: List[Assessment]
    ) -> Dict[str, any]:
        """
        Analyze consistency across multiple assessments.
        
        Args:
            assessments: List of assessments to analyze
            
        Returns:
            Dictionary with consistency analysis
        """
        if not assessments:
            return {}
        
        # Extract overall scores
        overall_scores = [a.overall_score.overall for a in assessments]
        
        # Extract criterion scores
        criterion_scores = {
            AssessmentCriterion.TASK_RESPONSE: [],
            AssessmentCriterion.COHERENCE_COHESION: [],
            AssessmentCriterion.LEXICAL_RESOURCE: [],
            AssessmentCriterion.GRAMMATICAL_RANGE: []
        }
        
        for assessment in assessments:
            for criterion in assessment.criteria_scores:
                criterion_name = criterion.criterion_name.lower().replace(" ", "_")
                if "task" in criterion_name:
                    criterion_scores[AssessmentCriterion.TASK_RESPONSE].append(criterion.score)
                elif "coherence" in criterion_name:
                    criterion_scores[AssessmentCriterion.COHERENCE_COHESION].append(criterion.score)
                elif "lexical" in criterion_name:
                    criterion_scores[AssessmentCriterion.LEXICAL_RESOURCE].append(criterion.score)
                elif "grammar" in criterion_name:
                    criterion_scores[AssessmentCriterion.GRAMMATICAL_RANGE].append(criterion.score)
        
        # Calculate consistency metrics
        overall_distribution = BandCalculator.calculate_score_distribution(overall_scores)
        
        criterion_distributions = {}
        for criterion, scores in criterion_scores.items():
            if scores:
                criterion_distributions[criterion.value] = BandCalculator.calculate_score_distribution(scores)
        
        # Calculate improvement trend
        improvement_trend = None
        if len(overall_scores) > 1:
            # Simple linear trend calculation
            x_values = list(range(len(overall_scores)))
            n = len(overall_scores)
            sum_x = sum(x_values)
            sum_y = sum(overall_scores)
            sum_xy = sum(x * y for x, y in zip(x_values, overall_scores))
            sum_x2 = sum(x * x for x in x_values)
            
            improvement_trend = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return {
            "overall_distribution": overall_distribution,
            "criterion_distributions": criterion_distributions,
            "improvement_trend": improvement_trend,
            "assessment_count": len(assessments),
            "consistency_score": 1 - (overall_distribution.get("std_dev", 0) / 2)  # Normalize to 0-1
        }


class ScoreValidator:
    """Validator for IELTS band scores and assessments."""
    
    @staticmethod
    def validate_assessment_scores(assessment: Assessment) -> Tuple[bool, List[str]]:
        """
        Validate all scores in an assessment.
        
        Args:
            assessment: Assessment to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate overall score
        if not CriteriaValidator.validate_band_score(assessment.overall_score.overall):
            errors.append(f"Invalid overall score: {assessment.overall_score.overall}")
        
        # Validate individual criterion scores
        for criterion in assessment.criteria_scores:
            if not CriteriaValidator.validate_band_score(criterion.score):
                errors.append(f"Invalid score for {criterion.criterion_name}: {criterion.score}")
        
        # Check score consistency
        criterion_scores = [c.score for c in assessment.criteria_scores]
        if criterion_scores:
            calculated_overall = BandCalculator.calculate_overall_score({
                AssessmentCriterion.TASK_RESPONSE: criterion_scores[0] if len(criterion_scores) > 0 else 0,
                AssessmentCriterion.COHERENCE_COHESION: criterion_scores[1] if len(criterion_scores) > 1 else 0,
                AssessmentCriterion.LEXICAL_RESOURCE: criterion_scores[2] if len(criterion_scores) > 2 else 0,
                AssessmentCriterion.GRAMMATICAL_RANGE: criterion_scores[3] if len(criterion_scores) > 3 else 0,
            })
            
            if abs(calculated_overall - assessment.overall_score.overall) > 0.5:
                errors.append(
                    f"Overall score ({assessment.overall_score.overall}) inconsistent with "
                    f"criterion scores (calculated: {calculated_overall})"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def suggest_score_corrections(assessment: Assessment) -> Assessment:
        """
        Suggest corrections for invalid scores in an assessment.
        
        Args:
            assessment: Assessment with potentially invalid scores
            
        Returns:
            Assessment with corrected scores
        """
        # Create a copy to avoid modifying the original
        corrected_assessment = Assessment(
            overall_score=assessment.overall_score,
            criteria_scores=assessment.criteria_scores.copy(),
            general_feedback=assessment.general_feedback,
            recommendations=assessment.recommendations,
            assessor_model=assessment.assessor_model
        )
        
        # Correct individual criterion scores
        for i, criterion in enumerate(corrected_assessment.criteria_scores):
            if not CriteriaValidator.validate_band_score(criterion.score):
                # Round to nearest valid score
                criterion.score = BandCalculator.round_to_band_score(criterion.score)
        
        # Recalculate overall score based on corrected criterion scores
        if corrected_assessment.criteria_scores:
            criterion_scores = {}
            for criterion in corrected_assessment.criteria_scores:
                criterion_name = criterion.criterion_name.lower().replace(" ", "_")
                if "task" in criterion_name:
                    criterion_scores[AssessmentCriterion.TASK_RESPONSE] = criterion.score
                elif "coherence" in criterion_name:
                    criterion_scores[AssessmentCriterion.COHERENCE_COHESION] = criterion.score
                elif "lexical" in criterion_name:
                    criterion_scores[AssessmentCriterion.LEXICAL_RESOURCE] = criterion.score
                elif "grammar" in criterion_name:
                    criterion_scores[AssessmentCriterion.GRAMMATICAL_RANGE] = criterion.score
            
            if criterion_scores:
                corrected_overall = BandCalculator.calculate_overall_score(criterion_scores)
                corrected_assessment.overall_score.overall = corrected_overall
        
        return corrected_assessment


class ScoreComparator:
    """Utility for comparing and analyzing score differences."""
    
    @staticmethod
    def compare_assessments(
        assessment1: Assessment, 
        assessment2: Assessment
    ) -> Dict[str, float]:
        """
        Compare two assessments and calculate differences.
        
        Args:
            assessment1: First assessment
            assessment2: Second assessment
            
        Returns:
            Dictionary with score differences
        """
        differences = {
            "overall_difference": assessment2.overall_score.overall - assessment1.overall_score.overall
        }
        
        # Compare criterion scores
        criteria1 = {c.criterion_name: c.score for c in assessment1.criteria_scores}
        criteria2 = {c.criterion_name: c.score for c in assessment2.criteria_scores}
        
        for criterion_name in set(criteria1.keys()) | set(criteria2.keys()):
            score1 = criteria1.get(criterion_name, 0)
            score2 = criteria2.get(criterion_name, 0)
            differences[f"{criterion_name}_difference"] = score2 - score1
        
        return differences
    
    @staticmethod
    def calculate_improvement_rate(
        assessments: List[Assessment], 
        time_period_days: int = 30
    ) -> float:
        """
        Calculate improvement rate over time.
        
        Args:
            assessments: List of assessments ordered by time
            time_period_days: Time period for rate calculation
            
        Returns:
            Improvement rate (points per day)
        """
        if len(assessments) < 2:
            return 0.0
        
        first_score = assessments[0].overall_score.overall
        last_score = assessments[-1].overall_score.overall
        
        improvement = last_score - first_score
        
        # Assume even distribution over time period
        return improvement / time_period_days if time_period_days > 0 else 0.0


# Convenience functions for common calculations
def calculate_band_score(criterion_scores: Dict[str, float]) -> BandScore:
    """
    Convenience function to calculate band scores from string-keyed dictionary.
    
    Args:
        criterion_scores: Dictionary with string keys for criteria
        
    Returns:
        BandScore object
    """
    # Convert string keys to AssessmentCriterion enum
    converted_scores = {}
    
    for key, score in criterion_scores.items():
        key_lower = key.lower().replace(" ", "_")
        if "task" in key_lower:
            converted_scores[AssessmentCriterion.TASK_RESPONSE] = score
        elif "coherence" in key_lower:
            converted_scores[AssessmentCriterion.COHERENCE_COHESION] = score
        elif "lexical" in key_lower:
            converted_scores[AssessmentCriterion.LEXICAL_RESOURCE] = score
        elif "grammar" in key_lower:
            converted_scores[AssessmentCriterion.GRAMMATICAL_RANGE] = score
    
    return BandCalculator.calculate_detailed_band_score(converted_scores)


def validate_and_correct_assessment(assessment: Assessment) -> Tuple[Assessment, List[str]]:
    """
    Convenience function to validate and correct an assessment.
    
    Args:
        assessment: Assessment to validate and correct
        
    Returns:
        Tuple of (corrected_assessment, list_of_corrections_made)
    """
    is_valid, errors = ScoreValidator.validate_assessment_scores(assessment)
    
    if is_valid:
        return assessment, []
    
    corrected_assessment = ScoreValidator.suggest_score_corrections(assessment)
    return corrected_assessment, errors
