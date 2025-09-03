"""
LLM provider configurations and constants.
"""

from typing import Dict, List, Optional
from enum import Enum

from ..core.models import LLMProvider


class ProviderCapabilities(Enum):
    """Provider capability flags."""
    CHAT_COMPLETION = "chat_completion"
    STREAMING = "streaming"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"


class ProviderConfig:
    """Configuration for LLM providers."""
    
    def __init__(
        self,
        provider: LLMProvider,
        base_url: Optional[str] = None,
        suggested_models: List[str] = None,
        requires_api_key: bool = True,
        default_api_key: Optional[str] = None,
        allow_custom_models: bool = True,
        capabilities: List[ProviderCapabilities] = None,
        max_tokens_limit: Optional[int] = None,
        supports_system_message: bool = True,
        rate_limit_rpm: Optional[int] = None
    ):
        """
        Initialize provider configuration.
        
        Args:
            provider: The LLM provider
            base_url: Base URL for API requests
            suggested_models: List of suggested model names
            requires_api_key: Whether API key is required
            default_api_key: Default API key (for local providers)
            allow_custom_models: Whether custom model names are allowed
            capabilities: List of provider capabilities
            max_tokens_limit: Maximum tokens supported
            supports_system_message: Whether system messages are supported
            rate_limit_rpm: Rate limit in requests per minute
        """
        self.provider = provider
        self.base_url = base_url
        self.suggested_models = suggested_models or []
        self.requires_api_key = requires_api_key
        self.default_api_key = default_api_key
        self.allow_custom_models = allow_custom_models
        self.capabilities = capabilities or [ProviderCapabilities.CHAT_COMPLETION]
        self.max_tokens_limit = max_tokens_limit
        self.supports_system_message = supports_system_message
        self.rate_limit_rpm = rate_limit_rpm
    
    def has_capability(self, capability: ProviderCapabilities) -> bool:
        """Check if provider has a specific capability."""
        return capability in self.capabilities
    
    def is_model_suggested(self, model: str) -> bool:
        """Check if a model is in the suggested list."""
        return model in self.suggested_models
    
    def validate_model(self, model: str) -> bool:
        """Validate model name for this provider."""
        if not model or not isinstance(model, str):
            return False
        
        # Basic validation - more specific validation can be added per provider
        if len(model.strip()) < 2:
            return False
        
        # If custom models are not allowed, check suggested list
        if not self.allow_custom_models:
            return self.is_model_suggested(model)
        
        return True


# Provider configurations
PROVIDER_CONFIGS: Dict[LLMProvider, ProviderConfig] = {
    LLMProvider.OPENAI: ProviderConfig(
        provider=LLMProvider.OPENAI,
        base_url=None,  # Uses OpenAI's default base URL
        suggested_models=[
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview", 
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        requires_api_key=True,
        allow_custom_models=True,
        capabilities=[
            ProviderCapabilities.CHAT_COMPLETION,
            ProviderCapabilities.STREAMING,
            ProviderCapabilities.FUNCTION_CALLING,
            ProviderCapabilities.VISION
        ],
        max_tokens_limit=4096,
        supports_system_message=True,
        rate_limit_rpm=3500  # Tier 1 limit for GPT-4
    ),
    
    LLMProvider.GOOGLE: ProviderConfig(
        provider=LLMProvider.GOOGLE,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        suggested_models=[
            "gemini-2.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision"
        ],
        requires_api_key=True,
        allow_custom_models=True,
        capabilities=[
            ProviderCapabilities.CHAT_COMPLETION,
            ProviderCapabilities.STREAMING,
            ProviderCapabilities.VISION
        ],
        max_tokens_limit=8192,
        supports_system_message=True,
        rate_limit_rpm=60  # Free tier limit
    ),
    
    LLMProvider.OLLAMA: ProviderConfig(
        provider=LLMProvider.OLLAMA,
        base_url="http://localhost:11434/v1",
        suggested_models=[
            "llama2",
            "llama3",
            "llama3:8b",
            "llama3:70b",
            "codellama",
            "codellama:7b",
            "codellama:13b",
            "mistral",
            "mistral:7b",
            "phi",
            "phi3",
            "qwen",
            "qwen:7b",
            "gemma",
            "gemma:7b"
        ],
        requires_api_key=False,
        default_api_key="ollama",
        allow_custom_models=True,
        capabilities=[ProviderCapabilities.CHAT_COMPLETION],
        max_tokens_limit=2048,  # Varies by model
        supports_system_message=True,
        rate_limit_rpm=None  # No rate limit for local deployment
    )
}


class ModelValidator:
    """Model validation utilities."""
    
    @staticmethod
    def validate_model_for_provider(provider: LLMProvider, model: str) -> bool:
        """
        Validate a model name for a specific provider.
        
        Args:
            provider: The LLM provider
            model: The model name to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        config = PROVIDER_CONFIGS.get(provider)
        if not config:
            return False
        
        return config.validate_model(model)
    
    @staticmethod
    def get_suggested_models(provider: LLMProvider) -> List[str]:
        """
        Get suggested models for a provider.
        
        Args:
            provider: The LLM provider
            
        Returns:
            List of suggested model names
        """
        config = PROVIDER_CONFIGS.get(provider)
        return config.suggested_models if config else []
    
    @staticmethod
    def allows_custom_models(provider: LLMProvider) -> bool:
        """
        Check if provider allows custom model names.
        
        Args:
            provider: The LLM provider
            
        Returns:
            bool: True if custom models are allowed
        """
        config = PROVIDER_CONFIGS.get(provider)
        return config.allow_custom_models if config else False
    
    @staticmethod
    def get_max_tokens_limit(provider: LLMProvider, model: str = None) -> Optional[int]:
        """
        Get maximum tokens limit for provider/model.
        
        Args:
            provider: The LLM provider
            model: Specific model name (optional)
            
        Returns:
            Maximum tokens limit or None if unlimited
        """
        config = PROVIDER_CONFIGS.get(provider)
        if not config:
            return None
        
        # Model-specific limits can be added here
        if provider == LLMProvider.OPENAI:
            if model and "gpt-4" in model.lower():
                if "32k" in model.lower():
                    return 32768
                elif "turbo" in model.lower():
                    return 4096
                else:
                    return 8192
            elif model and "gpt-3.5" in model.lower():
                if "16k" in model.lower():
                    return 16384
                else:
                    return 4096
        
        return config.max_tokens_limit
    
    @staticmethod
    def get_provider_capabilities(provider: LLMProvider) -> List[ProviderCapabilities]:
        """
        Get capabilities for a provider.
        
        Args:
            provider: The LLM provider
            
        Returns:
            List of provider capabilities
        """
        config = PROVIDER_CONFIGS.get(provider)
        return config.capabilities if config else []
    
    @staticmethod
    def supports_capability(provider: LLMProvider, capability: ProviderCapabilities) -> bool:
        """
        Check if provider supports a specific capability.
        
        Args:
            provider: The LLM provider
            capability: The capability to check
            
        Returns:
            bool: True if capability is supported
        """
        config = PROVIDER_CONFIGS.get(provider)
        return config.has_capability(capability) if config else False


class PromptTemplates:
    """Templates for IELTS assessment prompts."""
    
    IELTS_WRITING_TASK_2_SYSTEM_PROMPT = """You are an expert IELTS examiner with extensive experience in evaluating IELTS Writing Task 2 responses. Your role is to provide accurate, detailed, and constructive feedback following official IELTS assessment criteria.

ASSESSMENT CRITERIA:
1. Task Achievement (25%): How well the response addresses the task, presents a clear position, and supports ideas with relevant examples.
2. Coherence and Cohesion (25%): Logical organization, clear progression, appropriate use of cohesive devices, and effective paragraphing.
3. Lexical Resource (25%): Range and accuracy of vocabulary, appropriateness of word choice, and spelling accuracy.
4. Grammatical Range and Accuracy (25%): Range of grammatical structures, accuracy of grammar and punctuation, and error frequency/impact.

BAND SCORE DESCRIPTORS:
- Band 9: Expert user with full operational command
- Band 8: Very good user with fully operational command
- Band 7: Good user with operational command  
- Band 6: Competent user with generally effective command
- Band 5: Modest user with partial command
- Band 4: Limited user with limited command
- Band 3: Extremely limited user
- Band 2: Intermittent user
- Band 1: Non-user

RESPONSE FORMAT:
Provide your assessment in the following JSON format:
{
    "overall_score": {
        "overall": 7.0,
        "task_achievement": 7.0,
        "coherence_cohesion": 7.5,
        "lexical_resource": 6.5,
        "grammatical_range": 7.0
    },
    "criteria_scores": [
        {
            "criterion_name": "Task Achievement",
            "score": 7.0,
            "feedback": "Detailed feedback for this criterion...",
            "strengths": ["List of strengths"],
            "areas_for_improvement": ["List of areas to improve"]
        }
        // ... repeat for all criteria
    ],
    "general_feedback": "Overall feedback on the response...",
    "recommendations": ["List of specific recommendations for improvement"]
}

Be thorough, fair, and constructive in your assessment. Focus on both strengths and areas for improvement."""

    IELTS_WRITING_TASK_2_USER_PROMPT = """Please assess the following IELTS Writing Task 2 response according to official IELTS criteria:

TASK PROMPT:
{task_prompt}

CANDIDATE RESPONSE:
{user_response}

WORD COUNT: {word_count} words

Please provide a comprehensive assessment with specific feedback for each criterion, an overall band score, and actionable recommendations for improvement."""

    @classmethod
    def get_writing_task_2_prompt(cls, task_prompt: str, user_response: str, word_count: int) -> Dict[str, str]:
        """
        Get formatted prompts for Writing Task 2 assessment.
        
        Args:
            task_prompt: The original task prompt
            user_response: The user's response text
            word_count: Word count of the response
            
        Returns:
            Dictionary with system and user prompts
        """
        user_prompt = cls.IELTS_WRITING_TASK_2_USER_PROMPT.format(
            task_prompt=task_prompt,
            user_response=user_response,
            word_count=word_count
        )
        
        return {
            "system": cls.IELTS_WRITING_TASK_2_SYSTEM_PROMPT,
            "user": user_prompt
        }


def get_provider_config(provider: LLMProvider) -> Optional[ProviderConfig]:
    """
    Get configuration for a specific provider.
    
    Args:
        provider: The LLM provider
        
    Returns:
        Provider configuration or None if not found
    """
    return PROVIDER_CONFIGS.get(provider)


def list_all_suggested_models() -> Dict[LLMProvider, List[str]]:
    """
    Get all suggested models for all providers.
    
    Returns:
        Dictionary mapping providers to their suggested models
    """
    return {
        provider: config.suggested_models 
        for provider, config in PROVIDER_CONFIGS.items()
    }
