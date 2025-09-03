"""
LLM integration package for IELTS CLI application.
"""

from .providers import (
    LLMProvider,
    ProviderConfig,
    ProviderCapabilities,
    PROVIDER_CONFIGS,
    ModelValidator,
    PromptTemplates,
    get_provider_config,
    list_all_suggested_models
)

from .client import (
    LLMClient,
    LLMClientManager,
    LLMError,
    LLMConnectionError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMModelError,
    client_manager
)

__all__ = [
    # Providers
    "LLMProvider",
    "ProviderConfig",
    "ProviderCapabilities", 
    "PROVIDER_CONFIGS",
    "ModelValidator",
    "PromptTemplates",
    "get_provider_config",
    "list_all_suggested_models",
    
    # Client
    "LLMClient",
    "LLMClientManager",
    "LLMError",
    "LLMConnectionError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMModelError",
    "client_manager"
]
