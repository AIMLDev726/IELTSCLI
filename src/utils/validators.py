"""
Validation utilities for IELTS CLI application.
"""

import re
from typing import Dict, List, Optional, Union, Any
from email_validator import validate_email, EmailNotValidError


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Comprehensive input validation for IELTS CLI application."""
    
    @staticmethod
    def validate_api_key(api_key: str, provider: str = "openai") -> bool:
        """
        Validate API key format based on provider.
        
        Args:
            api_key: The API key to validate
            provider: The LLM provider (openai, google, ollama)
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the API key is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key cannot be empty")
        
        api_key = api_key.strip()
        
        if provider.lower() == "openai":
            # OpenAI API keys start with "sk-" and are typically 51 characters
            if not api_key.startswith("sk-"):
                raise ValidationError("OpenAI API key must start with 'sk-'")
            if len(api_key) < 40:
                raise ValidationError("OpenAI API key appears to be too short")
                
        elif provider.lower() == "google":
            # Google AI API keys are typically 39 characters
            if len(api_key) < 20:
                raise ValidationError("Google AI API key appears to be too short")
                
        elif provider.lower() == "ollama":
            # Ollama doesn't require real API keys, but we validate the format
            if api_key.lower() != "ollama" and len(api_key) < 3:
                raise ValidationError("Invalid Ollama API key")
        
        return True
    
    @staticmethod
    def validate_model_name(model_name: str) -> bool:
        """
        Validate model name format.
        
        Args:
            model_name: The model name to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the model name is invalid
        """
        if not model_name or not isinstance(model_name, str):
            raise ValidationError("Model name cannot be empty")
        
        model_name = model_name.strip()
        
        # Model names should be alphanumeric with hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9\-_.]+$', model_name):
            raise ValidationError(
                "Model name can only contain letters, numbers, hyphens, underscores, and dots"
            )
        
        if len(model_name) < 2:
            raise ValidationError("Model name must be at least 2 characters long")
        
        if len(model_name) > 100:
            raise ValidationError("Model name cannot exceed 100 characters")
        
        return True
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> bool:
        """
        Validate URL format.
        
        Args:
            url: The URL to validate
            allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the URL is invalid
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL cannot be empty")
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        url = url.strip()
        
        # Basic URL pattern validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url):
            raise ValidationError("Invalid URL format")
        
        # Check scheme
        scheme = url.split('://')[0].lower()
        if scheme not in allowed_schemes:
            raise ValidationError(f"URL scheme must be one of: {', '.join(allowed_schemes)}")
        
        return True
    
    @staticmethod
    def validate_word_count(text: str, min_words: int = 250, max_words: int = None) -> bool:
        """
        Validate word count for IELTS writing tasks.
        
        Args:
            text: The text to validate
            min_words: Minimum word count
            max_words: Maximum word count (optional)
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the word count is invalid
        """
        if not text or not isinstance(text, str):
            raise ValidationError("Text cannot be empty")
        
        # Count words (split by whitespace and filter out empty strings)
        words = [word for word in text.split() if word.strip()]
        word_count = len(words)
        
        if word_count < min_words:
            raise ValidationError(f"Text must contain at least {min_words} words (found {word_count})")
        
        if max_words and word_count > max_words:
            raise ValidationError(f"Text cannot exceed {max_words} words (found {word_count})")
        
        return True
    
    @staticmethod
    def validate_band_score(score: Union[int, float]) -> bool:
        """
        Validate IELTS band score.
        
        Args:
            score: The band score to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the band score is invalid
        """
        if score is None:
            raise ValidationError("Band score cannot be None")
        
        try:
            score = float(score)
        except (ValueError, TypeError):
            raise ValidationError("Band score must be a number")
        
        # IELTS scores range from 0 to 9 in 0.5 increments
        if score < 0 or score > 9:
            raise ValidationError("Band score must be between 0 and 9")
        
        # Check if score is in valid increments (0.5)
        if (score * 2) % 1 != 0:
            raise ValidationError("Band score must be in 0.5 increments")
        
        return True
    
    @staticmethod
    def validate_task_type(task_type: str) -> bool:
        """
        Validate IELTS task type.
        
        Args:
            task_type: The task type to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the task type is invalid
        """
        valid_task_types = [
            'writing_task_1_academic',
            'writing_task_1_general',
            'writing_task_2',
            'speaking_part_1',
            'speaking_part_2',
            'speaking_part_3',
            'reading_academic',
            'reading_general',
            'listening'
        ]
        
        if not task_type or not isinstance(task_type, str):
            raise ValidationError("Task type cannot be empty")
        
        task_type = task_type.lower().strip()
        
        if task_type not in valid_task_types:
            raise ValidationError(f"Invalid task type. Must be one of: {', '.join(valid_task_types)}")
        
        return True
    
    @staticmethod
    def validate_config_data(config: Dict[str, Any]) -> bool:
        """
        Validate configuration data structure.
        
        Args:
            config: The configuration dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValidationError("Configuration must be a dictionary")
        
        required_fields = ['llm_provider', 'model_configs', 'user_preferences']
        
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Missing required configuration field: {field}")
        
        # Validate provider
        valid_providers = ['openai', 'google', 'ollama']
        if config['llm_provider'] not in valid_providers:
            raise ValidationError(f"Invalid LLM provider. Must be one of: {', '.join(valid_providers)}")
        
        # Validate model configs
        if not isinstance(config['model_configs'], dict):
            raise ValidationError("Model configs must be a dictionary")
        
        # Validate user preferences
        if not isinstance(config['user_preferences'], dict):
            raise ValidationError("User preferences must be a dictionary")
        
        return True
    
    @staticmethod
    def validate_session_data(session: Dict[str, Any]) -> bool:
        """
        Validate session data structure.
        
        Args:
            session: The session dictionary to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the session data is invalid
        """
        if not isinstance(session, dict):
            raise ValidationError("Session data must be a dictionary")
        
        required_fields = ['task_type', 'user_response', 'timestamp']
        
        for field in required_fields:
            if field not in session:
                raise ValidationError(f"Missing required session field: {field}")
        
        # Validate task type
        InputValidator.validate_task_type(session['task_type'])
        
        # Validate user response
        if not session['user_response'] or not isinstance(session['user_response'], str):
            raise ValidationError("User response cannot be empty")
        
        return True
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize user input by removing potentially harmful content.
        
        Args:
            text: The text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
            
        Raises:
            ValidationError: If the input is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        # Remove null bytes and other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        if len(text) > max_length:
            raise ValidationError(f"Input cannot exceed {max_length} characters")
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Limit to 2 consecutive newlines
        text = re.sub(r' {2,}', ' ', text)      # Limit to single spaces
        
        return text.strip()
    
    @staticmethod
    def validate_temperature(temperature: Union[int, float]) -> bool:
        """
        Validate LLM temperature parameter.
        
        Args:
            temperature: The temperature value to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValidationError: If the temperature is invalid
        """
        if temperature is None:
            raise ValidationError("Temperature cannot be None")
        
        try:
            temperature = float(temperature)
        except (ValueError, TypeError):
            raise ValidationError("Temperature must be a number")
        
        if temperature < 0 or temperature > 2:
            raise ValidationError("Temperature must be between 0 and 2")
        
        return True
