"""
IELTS assessment criteria definitions and band score descriptors.
"""

from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass


class TaskType(str, Enum):
    """IELTS task types."""
    WRITING_TASK_1_ACADEMIC = "writing_task_1_academic"
    WRITING_TASK_1_GENERAL = "writing_task_1_general"
    WRITING_TASK_2 = "writing_task_2"


class AssessmentCriterion(str, Enum):
    """IELTS assessment criteria."""
    TASK_ACHIEVEMENT = "task_achievement"
    TASK_RESPONSE = "task_response"  # Alternative name for Task Achievement in Task 2
    COHERENCE_COHESION = "coherence_cohesion"
    LEXICAL_RESOURCE = "lexical_resource"
    GRAMMATICAL_RANGE = "grammatical_range"


@dataclass
class BandDescriptor:
    """Band score descriptor for a specific criterion and band level."""
    band: float
    criterion: AssessmentCriterion
    description: str
    key_features: List[str]
    typical_errors: List[str] = None
    
    def __post_init__(self):
        if self.typical_errors is None:
            self.typical_errors = []


class IELTSCriteria:
    """IELTS assessment criteria and band descriptors."""
    
    # Writing Task 2 - Task Achievement/Response Band Descriptors
    TASK_RESPONSE_DESCRIPTORS = {
        9.0: BandDescriptor(
            band=9.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Fully addresses all parts of the task with a fully developed position",
            key_features=[
                "Fully addresses all parts of the task",
                "Presents a fully developed position in answer to the question",
                "Ideas are relevant, fully extended and well supported",
                "Clear and comprehensive ideas throughout"
            ]
        ),
        8.0: BandDescriptor(
            band=8.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Sufficiently addresses all parts of the task with a well-developed position",
            key_features=[
                "Sufficiently addresses all parts of the task",
                "Presents a well-developed response to the question",
                "Ideas are relevant, well extended and supported",
                "Clear and effective ideas with occasional minor lapses"
            ]
        ),
        7.0: BandDescriptor(
            band=7.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Addresses all parts of the task with a clear position",
            key_features=[
                "Addresses all parts of the task",
                "Presents a clear position throughout the response",
                "Main ideas are well developed with relevant supporting details",
                "Ideas are generally clear and relevant"
            ]
        ),
        6.0: BandDescriptor(
            band=6.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Addresses all parts of the task although some may be more fully covered",
            key_features=[
                "Addresses all parts of the task although some may be more fully covered than others",
                "Presents a relevant position although conclusions may become unclear or repetitive",
                "Main ideas are relevant but may be insufficiently developed/unclear",
                "Some ideas may lack focus or contain inaccuracies"
            ]
        ),
        5.0: BandDescriptor(
            band=5.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Addresses the task only partially with limited development",
            key_features=[
                "Addresses the task only partially; format may be inappropriate in places",
                "Position unclear in places",
                "Main ideas are limited and not sufficiently developed",
                "Some irrelevant detail may be present"
            ]
        ),
        4.0: BandDescriptor(
            band=4.0,
            criterion=AssessmentCriterion.TASK_RESPONSE,
            description="Attempts to address the task but does not cover all requirements",
            key_features=[
                "Attempts to address the task but does not cover all requirements",
                "Position is unclear",
                "Few ideas and these are not well developed",
                "Significant irrelevant material or repetition"
            ]
        )
    }
    
    # Coherence and Cohesion Band Descriptors
    COHERENCE_COHESION_DESCRIPTORS = {
        9.0: BandDescriptor(
            band=9.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Logical sequencing with full cohesion and appropriate paragraphing",
            key_features=[
                "Uses cohesion in such a way that it attracts no attention",
                "Skilful management of paragraphing",
                "Sequences information and ideas logically",
                "Uses a wide range of cohesive devices appropriately"
            ]
        ),
        8.0: BandDescriptor(
            band=8.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Clear logical sequencing with effective cohesion and paragraphing",
            key_features=[
                "Sequences information and ideas logically",
                "Manages all aspects of cohesion well",
                "Uses paragraphing sufficiently and appropriately",
                "Uses a wide range of cohesive devices appropriately with only minor lapses"
            ]
        ),
        7.0: BandDescriptor(
            band=7.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Generally clear progression with appropriate use of cohesive devices",
            key_features=[
                "Logically organises information and ideas with clear progression throughout",
                "Uses a range of cohesive devices appropriately although there may be some under-/over-use",
                "Presents a clear central topic within each paragraph",
                "Generally appropriate paragraphing"
            ]
        ),
        6.0: BandDescriptor(
            band=6.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Coherent arrangement with some effective use of cohesive devices",
            key_features=[
                "Arranges information and ideas coherently with overall progression",
                "Uses cohesive devices effectively but cohesion within/between sentences may be faulty or mechanical",
                "May not always use referencing clearly or appropriately",
                "Uses paragraphing but not always logically"
            ]
        ),
        5.0: BandDescriptor(
            band=5.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Some organisation with limited range of cohesive devices",
            key_features=[
                "Presents information with some organisation but may lack overall progression",
                "Makes inadequate, inaccurate or over-use of cohesive devices",
                "May be repetitive because of lack of referencing and substitution",
                "May lack paragraphing or use inappropriate paragraphing"
            ]
        ),
        4.0: BandDescriptor(
            band=4.0,
            criterion=AssessmentCriterion.COHERENCE_COHESION,
            description="Limited organisation with minimal use of cohesive devices",
            key_features=[
                "Presents information and ideas but these are not arranged coherently",
                "Uses some basic cohesive devices but these may be inaccurate or repetitive",
                "May not write in paragraphs or their use may be confusing",
                "Lacks clear logical progression"
            ]
        )
    }
    
    # Lexical Resource Band Descriptors
    LEXICAL_RESOURCE_DESCRIPTORS = {
        9.0: BandDescriptor(
            band=9.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Wide range of vocabulary with natural and sophisticated language use",
            key_features=[
                "Uses a wide range of vocabulary with very natural and sophisticated control of lexical features",
                "Rare minor errors occur only as 'slips'",
                "Uses idiomatic language naturally and accurately",
                "Demonstrates sophisticated control of lexical features"
            ]
        ),
        8.0: BandDescriptor(
            band=8.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Wide range of vocabulary with good control and awareness of style",
            key_features=[
                "Uses a wide range of vocabulary fluently and flexibly to convey precise meanings",
                "Skilfully uses uncommon lexical items but occasional inaccuracies in word choice and collocation",
                "Produces rare errors in spelling and/or word formation",
                "Good awareness of style and collocation"
            ]
        ),
        7.0: BandDescriptor(
            band=7.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Sufficient range with good control and awareness of style",
            key_features=[
                "Uses a sufficient range of vocabulary to allow some flexibility and precise usage",
                "Uses less common lexical items with some awareness of style and collocation",
                "May produce occasional errors in word choice, spelling and/or word formation",
                "Generally good control of lexical features"
            ]
        ),
        6.0: BandDescriptor(
            band=6.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Adequate range with some errors that do not impede communication",
            key_features=[
                "Uses an adequate range of vocabulary for the task",
                "Attempts to use less common vocabulary but with some inaccuracy",
                "Makes some errors in spelling and/or word formation but they do not impede communication",
                "Some attempts at precise word choice"
            ]
        ),
        5.0: BandDescriptor(
            band=5.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Limited range with noticeable errors in word choice and spelling",
            key_features=[
                "Uses a limited range of vocabulary but this is minimally adequate for the task",
                "May make noticeable errors in spelling and/or word formation that may cause some difficulty",
                "Limited control of word formation and/or spelling",
                "Relies on basic vocabulary with some attempts at variety"
            ]
        ),
        4.0: BandDescriptor(
            band=4.0,
            criterion=AssessmentCriterion.LEXICAL_RESOURCE,
            description="Basic vocabulary with frequent errors",
            key_features=[
                "Uses only basic vocabulary which may be used repetitively",
                "May have little control of word formation and/or spelling",
                "Errors may cause strain for the reader",
                "Very limited range with frequent repetition"
            ]
        )
    }
    
    # Grammatical Range and Accuracy Band Descriptors
    GRAMMATICAL_RANGE_DESCRIPTORS = {
        9.0: BandDescriptor(
            band=9.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Wide range of structures with full flexibility and accurate usage",
            key_features=[
                "Uses a wide range of structures with full flexibility and accurate usage",
                "Rare minor errors occur only as 'slips'",
                "Accurate and appropriate punctuation throughout",
                "Complete grammatical control"
            ]
        ),
        8.0: BandDescriptor(
            band=8.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Wide range of structures with good control and few errors",
            key_features=[
                "Uses a wide range of structures flexibly",
                "Produces frequent error-free sentences",
                "Good control of grammar and punctuation but may make occasional errors",
                "Most sentences are error-free"
            ]
        ),
        7.0: BandDescriptor(
            band=7.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Variety of complex structures with good control and frequent error-free sentences",
            key_features=[
                "Uses a variety of complex structures",
                "Produces frequent error-free sentences",
                "Has good control of grammar and punctuation but may make a few errors",
                "Generally accurate with some errors that do not impede communication"
            ]
        ),
        6.0: BandDescriptor(
            band=6.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Mix of simple and complex structures with some accuracy",
            key_features=[
                "Uses a mix of simple and complex sentence forms",
                "Makes some errors in grammar and punctuation but they rarely reduce communication",
                "Generally maintains control of tense and sentence structure",
                "Some variety in sentence structure"
            ]
        ),
        5.0: BandDescriptor(
            band=5.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Limited range with frequent errors",
            key_features=[
                "Uses only a limited range of structures",
                "Attempts complex sentences but these tend to be less accurate than simple sentences",
                "May make frequent grammatical errors and punctuation may be faulty",
                "Errors can cause some difficulty for the reader"
            ]
        ),
        4.0: BandDescriptor(
            band=4.0,
            criterion=AssessmentCriterion.GRAMMATICAL_RANGE,
            description="Very limited range with frequent errors that may impede communication",
            key_features=[
                "Uses only a very limited range of structures",
                "Subordinate clauses are rare",
                "Some structures are accurate but errors predominate",
                "Errors frequently impede meaning"
            ]
        )
    }
    
    @classmethod
    def get_descriptor(
        self, 
        criterion: AssessmentCriterion, 
        band: float, 
        task_type: TaskType = TaskType.WRITING_TASK_2
    ) -> BandDescriptor:
        """
        Get band descriptor for a specific criterion and band level.
        
        Args:
            criterion: Assessment criterion
            band: Band score (0.0 to 9.0)
            task_type: IELTS task type
            
        Returns:
            Band descriptor
        """
        # Round to nearest 0.5 for descriptor lookup
        descriptor_band = round(band * 2) / 2
        
        if criterion == AssessmentCriterion.TASK_RESPONSE:
            descriptors = self.TASK_RESPONSE_DESCRIPTORS
        elif criterion == AssessmentCriterion.COHERENCE_COHESION:
            descriptors = self.COHERENCE_COHESION_DESCRIPTORS
        elif criterion == AssessmentCriterion.LEXICAL_RESOURCE:
            descriptors = self.LEXICAL_RESOURCE_DESCRIPTORS
        elif criterion == AssessmentCriterion.GRAMMATICAL_RANGE:
            descriptors = self.GRAMMATICAL_RANGE_DESCRIPTORS
        else:
            raise ValueError(f"Unknown criterion: {criterion}")
        
        # Find the best matching descriptor
        if descriptor_band in descriptors:
            return descriptors[descriptor_band]
        
        # Find closest descriptor if exact match not found
        available_bands = sorted(descriptors.keys(), reverse=True)
        for available_band in available_bands:
            if descriptor_band >= available_band:
                return descriptors[available_band]
        
        # Fallback to lowest band
        return descriptors[min(available_bands)]
    
    @classmethod
    def get_all_criteria(cls, task_type: TaskType = TaskType.WRITING_TASK_2) -> List[AssessmentCriterion]:
        """
        Get all assessment criteria for a task type.
        
        Args:
            task_type: IELTS task type
            
        Returns:
            List of assessment criteria
        """
        if task_type == TaskType.WRITING_TASK_2:
            return [
                AssessmentCriterion.TASK_RESPONSE,
                AssessmentCriterion.COHERENCE_COHESION,
                AssessmentCriterion.LEXICAL_RESOURCE,
                AssessmentCriterion.GRAMMATICAL_RANGE
            ]
        elif task_type in [TaskType.WRITING_TASK_1_ACADEMIC, TaskType.WRITING_TASK_1_GENERAL]:
            return [
                AssessmentCriterion.TASK_ACHIEVEMENT,
                AssessmentCriterion.COHERENCE_COHESION,
                AssessmentCriterion.LEXICAL_RESOURCE,
                AssessmentCriterion.GRAMMATICAL_RANGE
            ]
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    @classmethod
    def calculate_overall_score(cls, criterion_scores: Dict[AssessmentCriterion, float]) -> float:
        """
        Calculate overall band score from criterion scores.
        
        Args:
            criterion_scores: Dictionary of criterion scores
            
        Returns:
            Overall band score (rounded to nearest 0.5)
        """
        if not criterion_scores:
            return 0.0
        
        # All criteria have equal weight (25% each)
        total_score = sum(criterion_scores.values())
        average_score = total_score / len(criterion_scores)
        
        # Round to nearest 0.5
        return round(average_score * 2) / 2
    
    @classmethod
    def get_word_count_requirements(cls, task_type: TaskType) -> Tuple[int, int]:
        """
        Get word count requirements for a task type.
        
        Args:
            task_type: IELTS task type
            
        Returns:
            Tuple of (minimum_words, recommended_maximum)
        """
        if task_type == TaskType.WRITING_TASK_2:
            return (250, 350)
        elif task_type in [TaskType.WRITING_TASK_1_ACADEMIC, TaskType.WRITING_TASK_1_GENERAL]:
            return (150, 200)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    @classmethod
    def get_time_limit(cls, task_type: TaskType) -> int:
        """
        Get time limit in minutes for a task type.
        
        Args:
            task_type: IELTS task type
            
        Returns:
            Time limit in minutes
        """
        if task_type == TaskType.WRITING_TASK_2:
            return 40
        elif task_type in [TaskType.WRITING_TASK_1_ACADEMIC, TaskType.WRITING_TASK_1_GENERAL]:
            return 20
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    @classmethod
    def get_criterion_weight(cls, criterion: AssessmentCriterion) -> float:
        """
        Get weight for a specific criterion (all criteria are equally weighted).
        
        Args:
            criterion: Assessment criterion
            
        Returns:
            Weight as decimal (0.25 for all criteria)
        """
        return 0.25


class CriteriaValidator:
    """Validator for assessment criteria and scores."""
    
    @staticmethod
    def validate_band_score(score: float) -> bool:
        """
        Validate that a band score is in the correct range and increment.
        
        Args:
            score: Band score to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(score, (int, float)):
            return False
        
        if score < 0 or score > 9:
            return False
        
        # Check if score is in 0.5 increments
        return (score * 2) % 1 == 0
    
    @staticmethod
    def validate_criterion_scores(scores: Dict[AssessmentCriterion, float]) -> bool:
        """
        Validate a set of criterion scores.
        
        Args:
            scores: Dictionary of criterion scores
            
        Returns:
            True if all scores are valid, False otherwise
        """
        if not scores:
            return False
        
        for criterion, score in scores.items():
            if not isinstance(criterion, AssessmentCriterion):
                return False
            if not CriteriaValidator.validate_band_score(score):
                return False
        
        return True
    
    @staticmethod
    def get_score_level_description(score: float) -> str:
        """
        Get a general description of the score level.
        
        Args:
            score: Band score
            
        Returns:
            Description of the score level
        """
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.5:
            return "Very Good"
        elif score >= 6.5:
            return "Good"
        elif score >= 5.5:
            return "Competent"
        elif score >= 4.5:
            return "Modest"
        elif score >= 3.5:
            return "Limited"
        elif score >= 2.5:
            return "Extremely Limited"
        else:
            return "Intermittent/Non-user"
