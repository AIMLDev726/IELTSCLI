"""
Unified LLM client for IELTS CLI application supporting multiple providers.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
import aiohttp
from openai import AsyncOpenAI
import logging
from pydantic import BaseModel

from ..core.models import LLMProvider, ModelConfig
from ..core.config import config_manager
from .providers import (
    PROVIDER_CONFIGS, 
    ProviderConfig, 
    ModelValidator,
    PromptTemplates,
    ProviderCapabilities
)
from ..utils import display_error, display_warning, format_duration


# Configure logging
logger = logging.getLogger(__name__)


# Pydantic models for structured output
class OverallScore(BaseModel):
    overall: float
    task_achievement: float
    coherence_cohesion: float
    lexical_resource: float
    grammatical_range: float

class CriterionScore(BaseModel):
    criterion_name: str
    score: float
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]

class AssessmentResponse(BaseModel):
    overall_score: OverallScore
    criteria_scores: List[CriterionScore]
    general_feedback: str
    recommendations: List[str]


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMConnectionError(LLMError):
    """Exception for connection-related errors."""
    pass


class LLMAuthenticationError(LLMError):
    """Exception for authentication-related errors."""
    pass


class LLMRateLimitError(LLMError):
    """Exception for rate limit errors."""
    pass


class LLMModelError(LLMError):
    """Exception for model-related errors."""
    pass


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        if self.max_requests is None:
            return  # No rate limiting
        
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
            
            # Check if we can make a request
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = min(self.requests)
                wait_time = self.time_window - (now - oldest_request)
                
                if wait_time > 0:
                    logger.warning(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()  # Retry after waiting
            
            # Record this request
            self.requests.append(now)


class LLMClient:
    """Unified LLM client supporting multiple providers through OpenAI-compatible APIs."""
    
    def __init__(self, config_manager_or_provider=None, model_config: ModelConfig = None):
        """
        Initialize LLM client.
        
        Args:
            config_manager_or_provider: Either a ConfigManager instance or LLMProvider enum.
                                      If None, uses default configuration.
            model_config: Model configuration. If None, uses current configured model.
        """
        # Handle different input types
        if config_manager_or_provider is None:
            from ..core.config import config_manager as default_config_manager
            self.config_manager = default_config_manager
            self.provider = self.config_manager.config.llm_provider
            self.model_config = model_config or self.config_manager.get_current_model_config()
        elif hasattr(config_manager_or_provider, 'config'):
            # It's a ConfigManager instance
            self.config_manager = config_manager_or_provider
            self.provider = self.config_manager.config.llm_provider
            self.model_config = model_config or self.config_manager.get_current_model_config()
        else:
            # It's an LLMProvider enum
            from ..core.config import config_manager as default_config_manager
            self.config_manager = default_config_manager
            self.provider = config_manager_or_provider
            self.model_config = model_config or self.config_manager.get_current_model_config()
        
        self.provider_config = PROVIDER_CONFIGS.get(self.provider)
        
        if not self.provider_config:
            raise LLMError(f"Unsupported provider: {self.provider}")
        
        # Initialize OpenAI client with provider-specific configuration
        self._init_client()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=self.provider_config.rate_limit_rpm,
            time_window=60
        )
        
        # Request tracking
        self.request_count = 0
        self.total_tokens_used = 0
        self.last_request_time = None
    
    def _init_client(self) -> None:
        """Initialize the OpenAI client with provider-specific configuration."""
        try:
            # Get API key
            api_key = self.model_config.api_key
            if not api_key and self.provider_config.requires_api_key:
                # Try to get from secure storage
                api_key = self.config_manager.secure_storage.retrieve(f"{self.provider.value}_api_key")
                if not api_key:
                    raise LLMAuthenticationError(f"No API key configured for {self.provider.value}")
            elif not api_key:
                api_key = self.provider_config.default_api_key or "dummy"
            
            # Configure base URL
            base_url = self.model_config.base_url or self.provider_config.base_url
            
            # Initialize OpenAI client
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=30.0
            )
            
            logger.info(f"Initialized LLM client for {self.provider.value} with model {self.model_config.model}")
            
        except Exception as e:
            raise LLMError(f"Failed to initialize LLM client: {e}")
    
    async def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to the LLM provider.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            start_time = time.time()
            
            # Simple test message
            messages = [
                {"role": "user", "content": "Say 'Hello' in response to this test message."}
            ]
            
            await self.rate_limiter.acquire()
            
            response = await self.client.chat.completions.create(
                model=self.model_config.model,
                messages=messages,
                max_tokens=10,
                temperature=0.1
            )
            
            duration = time.time() - start_time
            
            if response.choices and response.choices[0].message:
                return True, f"Connection successful ({format_duration(duration)})"
            else:
                return False, "No response received from model"
                
        except Exception as e:
            error_msg = str(e)
            
            # Classify error types
            if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return False, f"Authentication failed: {error_msg}"
            elif "rate limit" in error_msg.lower():
                return False, f"Rate limit exceeded: {error_msg}"
            elif "not found" in error_msg.lower() or "model" in error_msg.lower():
                return False, f"Model not found: {error_msg}"
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return False, f"Connection failed: {error_msg}"
            else:
                return False, f"Test failed: {error_msg}"
    
    async def assess_ielts_response(
        self, 
        task_prompt: str, 
        user_response: str, 
        task_type: str = "writing_task_2"
    ) -> Dict[str, Any]:
        """
        Assess an IELTS response using the configured LLM.
        
        Args:
            task_prompt: The original IELTS task prompt
            user_response: The user's response to assess
            task_type: Type of IELTS task (currently only writing_task_2 supported)
            
        Returns:
            Assessment result as dictionary
            
        Raises:
            LLMError: If assessment fails
        """
        try:
            # Validate inputs
            if not task_prompt or not user_response:
                raise ValueError("Task prompt and user response cannot be empty")
            
            # Calculate word count
            word_count = len(user_response.split())
            
            # Get prompts based on task type
            if task_type == "writing_task_2":
                prompts = PromptTemplates.get_writing_task_2_prompt(
                    task_prompt, user_response, word_count
                )
            else:
                raise LLMError(f"Unsupported task type: {task_type}")
            
            # Prepare messages
            messages = [
                {"role": "system", "content": prompts["system"]},
                {"role": "user", "content": prompts["user"]}
            ]
            
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            start_time = time.time()
            
            # Make API request with structured output
            response = await self.client.chat.completions.create(
                model=self.model_config.model,
                messages=messages,
                temperature=self.model_config.temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ielts_assessment",
                        "strict": True,
                        "schema": AssessmentResponse.model_json_schema()
                    }
                }
            )
            
            duration = time.time() - start_time
            self.last_request_time = time.time()
            self.request_count += 1
            
            if response.usage:
                self.total_tokens_used += response.usage.total_tokens
            
            # Extract response content
            if not response.choices or not response.choices[0].message:
                logger.error(f"No response choices from model. Full response: {response}")
                raise LLMError("No response received from model")
            
            content = response.choices[0].message.content
            
            if content is None:
                logger.error(f"LLM response content is None. Full response: {response}")
                raise LLMError("LLM returned empty content")
            
            # Parse JSON response (guaranteed to be valid JSON with structured output)
            try:
                assessment = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response content: {content}")
                raise LLMError(f"Invalid JSON response: {e}")
            
            # Add metadata
            assessment["metadata"] = {
                "provider": self.provider.value,
                "model": self.model_config.model,
                "task_type": task_type,
                "word_count": word_count,
                "assessment_duration": duration,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
            logger.info(f"Assessment completed in {format_duration(duration)}")
            
            return assessment
            
        except Exception as e:
            if isinstance(e, LLMError):
                raise
            else:
                raise LLMError(f"Assessment failed: {e}")
    
    async def generate_writing_prompt(self, difficulty_level: str = "medium") -> str:
        """
        Generate a Writing Task 2 prompt.
        
        Args:
            difficulty_level: Difficulty level (easy, medium, hard)
            
        Returns:
            Generated IELTS Writing Task 2 prompt
        """
        try:
            prompt = f"""Generate an IELTS Writing Task 2 prompt at {difficulty_level} difficulty level.

The prompt should:
1. Be appropriate for IELTS Academic Writing Task 2
2. Present a clear opinion, discussion, or problem-solution task
3. Be relevant to contemporary issues
4. Allow for balanced argumentation
5. Be at {difficulty_level} difficulty level

Format the response as a complete IELTS task instruction including:
- Clear task statement
- Minimum word count requirement (250 words)
- Time allocation (40 minutes)

Provide only the task prompt, no additional explanation."""

            messages = [{"role": "user", "content": prompt}]
            
            await self.rate_limiter.acquire()
            
    
            
            response = await self.client.chat.completions.create(
                model=self.model_config.model,
                messages=messages,
                temperature=0.8,  # Higher creativity for prompt generation
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                if content:
                    return content.strip()
                else:
                    # For Gemini thinking models, check if it's a MAX_TOKENS issue
                    finish_reason = getattr(response.choices[0], 'finish_reason', None)
                    if finish_reason == 'max_tokens':
                        logger.warning("Response truncated due to max_tokens limit. Retrying with higher limit...")
                        # Retry with higher max_tokens
                        response = await self.client.chat.completions.create(
                            model=self.model_config.model,
                            messages=messages,
                            temperature=0.8,
                        )
                        content = response.choices[0].message.content if response.choices and response.choices[0].message else None
                        if content:
                            return content.strip()
                    
                    logger.error(f"Empty response content. Model: {self.model_config.model}, Finish reason: {finish_reason}")
                    logger.error(f"Full response: {response}")
                    raise LLMError("Empty response content from LLM")
            else:
                raise LLMError("No response choices or message from LLM")
                
        except Exception as e:
            raise LLMError(f"Prompt generation failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client usage statistics.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            "provider": self.provider.value,
            "model": self.model_config.model,
            "request_count": self.request_count,
            "total_tokens_used": self.total_tokens_used,
            "last_request_time": self.last_request_time,
            "rate_limit_rpm": self.provider_config.rate_limit_rpm
        }
    
    async def close(self) -> None:
        """Close the client and cleanup resources."""
        try:
            if hasattr(self.client, 'close'):
                await self.client.close()
        except Exception as e:
            logger.warning(f"Error closing LLM client: {e}")


class LLMClientManager:
    """Manager for LLM clients with connection pooling and fallback support."""
    
    def __init__(self):
        """Initialize the client manager."""
        self._clients: Dict[LLMProvider, LLMClient] = {}
        self._current_client: Optional[LLMClient] = None
    
    async def get_client(self, provider: LLMProvider = None) -> LLMClient:
        """
        Get or create an LLM client for the specified provider.
        
        Args:
            provider: LLM provider. If None, uses current configured provider.
            
        Returns:
            LLM client instance
        """
        provider = provider or config_manager.config.llm_provider
        
        if provider not in self._clients:
            self._clients[provider] = LLMClient(provider)
        
        self._current_client = self._clients[provider]
        return self._current_client
    
    async def test_all_providers(self) -> Dict[LLMProvider, Tuple[bool, str]]:
        """
        Test connection to all configured providers.
        
        Returns:
            Dictionary mapping providers to test results
        """
        results = {}
        
        for provider in LLMProvider:
            if config_manager.is_provider_configured(provider):
                try:
                    client = await self.get_client(provider)
                    results[provider] = await client.test_connection()
                except Exception as e:
                    results[provider] = (False, f"Failed to create client: {e}")
            else:
                results[provider] = (False, "Provider not configured")
        
        return results
    
    async def assess_with_fallback(
        self, 
        task_prompt: str, 
        user_response: str,
        task_type: str = "writing_task_2",
        preferred_providers: List[LLMProvider] = None
    ) -> Tuple[Dict[str, Any], LLMProvider]:
        """
        Assess response with fallback to other providers if primary fails.
        
        Args:
            task_prompt: The IELTS task prompt
            user_response: User's response
            task_type: Type of IELTS task
            preferred_providers: List of providers to try in order
            
        Returns:
            Tuple of (assessment_result, successful_provider)
        """
        if preferred_providers is None:
            preferred_providers = config_manager.list_configured_providers()
            # Move current provider to front
            current = config_manager.config.llm_provider
            if current in preferred_providers:
                preferred_providers.remove(current)
                preferred_providers.insert(0, current)
        
        last_error = None
        
        for provider in preferred_providers:
            try:
                client = await self.get_client(provider)
                assessment = await client.assess_ielts_response(
                    task_prompt, user_response, task_type
                )
                return assessment, provider
                
            except Exception as e:
                last_error = e
                logger.warning(f"Assessment failed with {provider.value}: {e}")
                continue
        
        # All providers failed
        raise LLMError(f"Assessment failed with all providers. Last error: {last_error}")
    
    async def close_all(self) -> None:
        """Close all client connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()
        self._current_client = None


# Global client manager instance
client_manager = LLMClientManager()
