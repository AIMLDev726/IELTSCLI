"""
IELTS response analysis engine for processing and evaluating user responses.
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..core.models import (
    Assessment, 
    AssessmentCriteria, 
    BandScore, 
    UserResponse,
    TaskType as ModelTaskType
)
from .criteria import (
    IELTSCriteria, 
    AssessmentCriterion, 
    TaskType, 
    CriteriaValidator
)
# Import directly to avoid circular imports
from ..llm.client import LLMClient, LLMError
from ..utils import display_warning, format_duration


class AnalysisError(Exception):
    """Exception raised for analysis-related errors."""
    pass


class ResponseAnalyzer:
    """Analyzes IELTS responses and converts LLM feedback into structured assessments."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the response analyzer.
        
        Args:
            llm_client: LLM client for assessment
        """
        self.llm_client = llm_client
        self.criteria_map = {
            # Map different naming conventions to standard criteria
            "task_achievement": AssessmentCriterion.TASK_RESPONSE,
            "task_response": AssessmentCriterion.TASK_RESPONSE,
            "coherence_cohesion": AssessmentCriterion.COHERENCE_COHESION,
            "coherence_and_cohesion": AssessmentCriterion.COHERENCE_COHESION,
            "lexical_resource": AssessmentCriterion.LEXICAL_RESOURCE,
            "grammatical_range": AssessmentCriterion.GRAMMATICAL_RANGE,
            "grammatical_range_and_accuracy": AssessmentCriterion.GRAMMATICAL_RANGE
        }
    
    def analyze_text_metrics(self, text: str) -> Dict[str, Any]:
        """
        Analyze basic text metrics.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with text metrics
        """
        if not text:
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "average_sentence_length": 0,
                "average_word_length": 0
            }
        
        # Basic counts
        word_count = len(text.split())
        character_count = len(text)
        
        # Sentence count (approximate)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Paragraph count
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Averages
        average_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        words = text.split()
        average_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        return {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "average_sentence_length": round(average_sentence_length, 1),
            "average_word_length": round(average_word_length, 1)
        }
    
    def extract_vocabulary_features(self, text: str) -> Dict[str, Any]:
        """
        Extract vocabulary-related features from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with vocabulary features
        """
        if not text:
            return {
                "unique_words": 0,
                "lexical_diversity": 0,
                "long_words_percentage": 0,
                "complex_words": []
            }
        
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        
        # Lexical diversity (Type-Token Ratio)
        lexical_diversity = len(unique_words) / len(words) if words else 0
        
        # Long words (6+ characters)
        long_words = [word for word in words if len(word) >= 6]
        long_words_percentage = len(long_words) / len(words) * 100 if words else 0
        
        # Complex/academic words (simple heuristic)
        complex_words = [word for word in unique_words if len(word) >= 8]
        
        return {
            "unique_words": len(unique_words),
            "lexical_diversity": round(lexical_diversity, 3),
            "long_words_percentage": round(long_words_percentage, 1),
            "complex_words": sorted(list(complex_words))[:10]  # Top 10 for brevity
        }
    
    def detect_structural_features(self, text: str) -> Dict[str, Any]:
        """
        Detect structural features in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with structural features
        """
        # Common transition words and phrases
        transitions = [
            "however", "moreover", "furthermore", "additionally", "consequently",
            "therefore", "thus", "hence", "nevertheless", "nonetheless",
            "in contrast", "on the other hand", "for instance", "for example",
            "in conclusion", "to summarize", "firstly", "secondly", "finally"
        ]
        
        text_lower = text.lower()
        
        # Count transitions
        transition_count = sum(1 for transition in transitions if transition in text_lower)
        
        # Detect introduction and conclusion patterns
        has_introduction = any(phrase in text_lower[:200] for phrase in [
            "in my opinion", "i believe", "this essay", "the question of", "nowadays"
        ])
        
        has_conclusion = any(phrase in text_lower[-200:] for phrase in [
            "in conclusion", "to conclude", "in summary", "to summarize", "overall"
        ])
        
        # Basic paragraph structure analysis
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        
        return {
            "transition_words_count": transition_count,
            "has_clear_introduction": has_introduction,
            "has_clear_conclusion": has_conclusion,
            "paragraph_count": len(paragraphs),
            "paragraph_word_counts": paragraph_lengths,
            "balanced_paragraphs": len(set(paragraph_lengths)) <= 2 if paragraph_lengths else False
        }
    
    def validate_llm_response(self, llm_response: Dict[str, Any]) -> bool:
        """
        Validate LLM assessment response structure.
        
        Args:
            llm_response: Response from LLM
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            required_fields = ["overall_score", "criteria_scores", "general_feedback"]
            for field in required_fields:
                if field not in llm_response:
                    display_warning(f"Missing required field: {field}")
                    return False
            
            # Validate overall_score structure
            overall_score = llm_response["overall_score"]
            if not isinstance(overall_score, dict):
                display_warning("overall_score must be a dictionary")
                return False
            
            if "overall" not in overall_score:
                display_warning("Missing 'overall' in overall_score")
                return False
            
            if not CriteriaValidator.validate_band_score(overall_score["overall"]):
                display_warning(f"Invalid overall band score: {overall_score['overall']}")
                return False
            
            # Validate criteria_scores structure
            criteria_scores = llm_response["criteria_scores"]
            if not isinstance(criteria_scores, list):
                display_warning("criteria_scores must be a list")
                return False
            
            for criterion in criteria_scores:
                if not isinstance(criterion, dict):
                    display_warning("Each criterion must be a dictionary")
                    return False
                
                required_criterion_fields = ["criterion_name", "score", "feedback"]
                for field in required_criterion_fields:
                    if field not in criterion:
                        display_warning(f"Missing required criterion field: {field}")
                        return False
                
                if not CriteriaValidator.validate_band_score(criterion["score"]):
                    display_warning(f"Invalid criterion score: {criterion['score']}")
                    return False
            
            return True
            
        except Exception as e:
            display_warning(f"Error validating LLM response: {e}")
            return False
    
    def normalize_criterion_name(self, criterion_name: str) -> AssessmentCriterion:
        """
        Normalize criterion name to standard format.
        
        Args:
            criterion_name: Raw criterion name from LLM
            
        Returns:
            Normalized assessment criterion
        """
        normalized = criterion_name.lower().replace(" ", "_").replace("&", "and")
        
        if normalized in self.criteria_map:
            return self.criteria_map[normalized]
        
        # Fallback matching
        if "task" in normalized:
            return AssessmentCriterion.TASK_RESPONSE
        elif "coherence" in normalized or "cohesion" in normalized:
            return AssessmentCriterion.COHERENCE_COHESION
        elif "lexical" in normalized or "vocabulary" in normalized:
            return AssessmentCriterion.LEXICAL_RESOURCE
        elif "grammar" in normalized or "grammatical" in normalized:
            return AssessmentCriterion.GRAMMATICAL_RANGE
        else:
            # Default fallback
            return AssessmentCriterion.TASK_RESPONSE
    
    def parse_llm_assessment(self, llm_response: Dict[str, Any]) -> Assessment:
        """
        Parse LLM response into structured Assessment object.
        
        Args:
            llm_response: Raw response from LLM
            
        Returns:
            Structured Assessment object
            
        Raises:
            AnalysisError: If parsing fails
        """
        try:
            # Validate response structure
            if not self.validate_llm_response(llm_response):
                raise AnalysisError("Invalid LLM response structure")
            
            # Parse overall scores
            overall_score_data = llm_response["overall_score"]
            overall_band_score = overall_score_data["overall"]
            
            # Parse criteria scores
            criteria_scores = []
            for criterion_data in llm_response["criteria_scores"]:
                criterion = AssessmentCriteria(
                    criterion_name=criterion_data["criterion_name"],
                    score=criterion_data["score"],
                    feedback=criterion_data["feedback"],
                    strengths=criterion_data.get("strengths", []),
                    areas_for_improvement=criterion_data.get("areas_for_improvement", [])
                )
                criteria_scores.append(criterion)
            
            # Create assessment
            assessment = Assessment(
                overall_band_score=overall_band_score,
                criteria_scores=criteria_scores,
                overall_feedback=llm_response["general_feedback"],
                recommendations=llm_response.get("recommendations", []),
                assessor_model=llm_response.get("metadata", {}).get("model", "unknown")
            )
            
            return assessment
            
        except Exception as e:
            raise AnalysisError(f"Failed to parse LLM assessment: {e}")
    
    def enhance_assessment_with_metrics(
        self, 
        assessment: Assessment, 
        user_response: UserResponse,
        task_type: str = "writing_task_2"
    ) -> Assessment:
        """
        Enhance assessment with additional text metrics and analysis.
        
        Args:
            assessment: Base assessment from LLM
            user_response: User's response
            task_type: Type of IELTS task
            
        Returns:
            Enhanced assessment with additional insights
        """
        try:
            # Analyze text metrics
            text_metrics = self.analyze_text_metrics(user_response.text)
            vocab_features = self.extract_vocabulary_features(user_response.text)
            structural_features = self.detect_structural_features(user_response.text)
            
            # Add word count validation feedback
            if task_type == "writing_task_2":
                min_words, max_words = 250, 350
                word_count = text_metrics["word_count"]
                
                if word_count < min_words:
                    assessment.recommendations.append(
                        f"Increase word count to at least {min_words} words (current: {word_count})"
                    )
                elif word_count > max_words + 50:  # Allow some flexibility
                    assessment.recommendations.append(
                        f"Consider reducing word count for better time management (current: {word_count})"
                    )
            
            # Add vocabulary insights
            if vocab_features["lexical_diversity"] < 0.4:
                assessment.recommendations.append(
                    "Try to use more varied vocabulary to improve lexical diversity"
                )
            
            # Add structural insights
            if not structural_features["has_clear_introduction"]:
                assessment.recommendations.append(
                    "Consider adding a clearer introduction that states your position"
                )
            
            if not structural_features["has_clear_conclusion"]:
                assessment.recommendations.append(
                    "Add a clear conclusion that summarizes your main points"
                )
            
            if structural_features["transition_words_count"] < 3:
                assessment.recommendations.append(
                    "Use more transition words to improve coherence and cohesion"
                )
            
            return assessment
            
        except Exception as e:
            display_warning(f"Failed to enhance assessment with metrics: {e}")
            return assessment
    
    async def analyze_response(
        self,
        task_prompt: str,
        user_response: UserResponse,
        task_type: str = "writing_task_2"
    ) -> Assessment:
        """
        Perform complete analysis of an IELTS response.
        
        Args:
            task_prompt: The original task prompt
            user_response: User's response to analyze
            task_type: Type of IELTS task
            
        Returns:
            Complete assessment of the response
            
        Raises:
            AnalysisError: If analysis fails
        """
        try:
            start_time = datetime.now()
            
            # Get LLM assessment
            llm_response = await self.llm_client.assess_ielts_response(
                task_prompt=task_prompt,
                user_response=user_response.text,
                task_type=task_type
            )
            
            # Parse LLM response
            assessment = self.parse_llm_assessment(llm_response)
            
            # Enhance with additional metrics
            assessment = self.enhance_assessment_with_metrics(
                assessment, user_response, task_type
            )
            
            duration = datetime.now() - start_time
            
            # Add analysis metadata
            if hasattr(assessment, 'metadata') and assessment.metadata:
                assessment.metadata.update({
                    "analysis_duration": duration.total_seconds(),
                    "enhanced_with_metrics": True
                })
            
            return assessment
            
        except LLMError as e:
            raise AnalysisError(f"LLM assessment failed: {e}")
        except Exception as e:
            raise AnalysisError(f"Response analysis failed: {e}")
    
    def generate_improvement_suggestions(
        self, 
        assessment: Assessment,
        task_type: str = "writing_task_2"
    ) -> List[str]:
        """
        Generate specific improvement suggestions based on assessment.
        
        Args:
            assessment: Assessment result
            task_type: Type of IELTS task
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        try:
            # Analyze scores to identify weakest areas
            criterion_scores = {
                criterion.criterion_name: criterion.score 
                for criterion in assessment.criteria_scores
            }
            
            if criterion_scores:
                # Find the lowest scoring criterion
                lowest_criterion = min(criterion_scores.items(), key=lambda x: x[1])
                lowest_score = lowest_criterion[1]
                
                if lowest_score < 6.0:
                    suggestions.append(
                        f"Focus on improving {lowest_criterion[0].replace('_', ' ').title()} "
                        f"(current score: {lowest_score})"
                    )
                
                # Specific suggestions based on criteria
                for criterion in assessment.criteria_scores:
                    if criterion.score < 6.0:
                        if "task" in criterion.criterion_name.lower():
                            suggestions.extend([
                                "Practice addressing all parts of the task more completely",
                                "Develop your ideas with more specific examples and details",
                                "Ensure your position is clear throughout the response"
                            ])
                        elif "coherence" in criterion.criterion_name.lower():
                            suggestions.extend([
                                "Use more linking words and phrases to connect ideas",
                                "Organize your paragraphs more logically",
                                "Practice clear topic sentences for each paragraph"
                            ])
                        elif "lexical" in criterion.criterion_name.lower():
                            suggestions.extend([
                                "Learn and practice using more academic vocabulary",
                                "Focus on precise word choice and collocation",
                                "Review common spelling patterns and word formation"
                            ])
                        elif "grammatical" in criterion.criterion_name.lower():
                            suggestions.extend([
                                "Practice using a variety of sentence structures",
                                "Review common grammar patterns and their usage",
                                "Pay attention to verb tenses and subject-verb agreement"
                            ])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_suggestions = []
            for suggestion in suggestions:
                if suggestion not in seen:
                    seen.add(suggestion)
                    unique_suggestions.append(suggestion)
            
            return unique_suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            display_warning(f"Failed to generate improvement suggestions: {e}")
            return ["Continue practicing writing tasks to improve overall performance"]


# Note: Global analyzer instance removed due to LLM client requirement
# Create ResponseAnalyzer instances with proper LLM client as needed
