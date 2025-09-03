"""
Configuration management for IELTS CLI application.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .models import AppConfig, ModelConfig, UserPreferences, LLMProvider
from ..utils import (
    get_app_data_dir, 
    ensure_app_data_dir, 
    display_error, 
    display_success,
    ValidationError,
    InputValidator
)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class SecureStorage:
    """Secure storage for sensitive configuration data like API keys."""
    
    def __init__(self, password: str = None):
        """
        Initialize secure storage.
        
        Args:
            password: Password for encryption. If None, uses machine-specific key.
        """
        self.app_dir = ensure_app_data_dir()
        self.key_file = self.app_dir / "storage.key"
        self.data_file = self.app_dir / "secure_data.enc"
        
        if password:
            self._key = self._derive_key_from_password(password)
        else:
            self._key = self._get_or_create_key()
        
        self._cipher = Fernet(self._key)
    
    def _derive_key_from_password(self, password: str) -> bytes:
        """Derive encryption key from password."""
        password_bytes = password.encode('utf-8')
        salt = b'ieltscli_salt_2024'  # In production, use random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create a new one."""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            # Set restrictive permissions (Windows and Unix)
            try:
                if os.name != 'nt':  # Unix-like systems
                    os.chmod(self.key_file, 0o600)
            except OSError:
                pass  # Ignore permission errors on some systems
            return key
    
    def store(self, key: str, value: str) -> None:
        """
        Store encrypted data.
        
        Args:
            key: Storage key
            value: Value to encrypt and store
        """
        data = self._load_data()
        data[key] = value
        self._save_data(data)
    
    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve and decrypt data.
        
        Args:
            key: Storage key
            
        Returns:
            Decrypted value or None if not found
        """
        data = self._load_data()
        return data.get(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete stored data.
        
        Args:
            key: Storage key
            
        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        if key in data:
            del data[key]
            self._save_data(data)
            return True
        return False
    
    def list_keys(self) -> list:
        """List all stored keys."""
        data = self._load_data()
        return list(data.keys())
    
    def _load_data(self) -> Dict[str, str]:
        """Load and decrypt stored data."""
        if not self.data_file.exists():
            return {}
        
        try:
            encrypted_data = self.data_file.read_bytes()
            decrypted_data = self._cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ConfigurationError(f"Failed to load secure data: {e}")
    
    def _save_data(self, data: Dict[str, str]) -> None:
        """Encrypt and save data."""
        try:
            json_data = json.dumps(data)
            encrypted_data = self._cipher.encrypt(json_data.encode('utf-8'))
            self.data_file.write_bytes(encrypted_data)
            
            # Set restrictive permissions
            try:
                if os.name != 'nt':  # Unix-like systems
                    os.chmod(self.data_file, 0o600)
            except OSError:
                pass
        except Exception as e:
            raise ConfigurationError(f"Failed to save secure data: {e}")


class ConfigManager:
    """Manages application configuration with secure storage for sensitive data."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.app_dir = ensure_app_data_dir()
        self.config_file = self.app_dir / "config.json"
        self.secure_storage = SecureStorage()
        self._config: Optional[AppConfig] = None
    
    @property
    def config(self) -> AppConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> AppConfig:
        """
        Load configuration from file.
        
        Returns:
            AppConfig: The loaded configuration
            
        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            if not self.config_file.exists():
                return self._create_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load API keys from secure storage
            self._load_api_keys(config_data)
            
            # Validate and create AppConfig instance
            config = AppConfig(**config_data)
            
            # Update any missing default values
            self._update_config_if_needed(config)
            
            return config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: AppConfig = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save. If None, saves current config.
            
        Raises:
            ConfigurationError: If configuration saving fails
        """
        if config is None:
            config = self.config
        
        try:
            # Update timestamp
            config.update_timestamp()
            
            # Save API keys to secure storage and remove from config data
            config_data = config.dict()
            self._save_api_keys(config_data)
            
            # Save configuration to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            # Set restrictive permissions
            try:
                if os.name != 'nt':  # Unix-like systems
                    os.chmod(self.config_file, 0o600)
            except OSError:
                pass
            
            self._config = config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def _create_default_config(self) -> AppConfig:
        """Create default configuration."""
        default_model_configs = {
            LLMProvider.OPENAI: ModelConfig(
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000
            ),
            LLMProvider.GOOGLE: ModelConfig(
                model="gemini-2.5-flash", 
                temperature=0.7,
                max_tokens=2000,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            ),
            LLMProvider.OLLAMA: ModelConfig(
                model="llama2",
                api_key="ollama",
                temperature=0.7,
                max_tokens=2000,
                base_url="http://localhost:11434/v1"
            )
        }
        
        config = AppConfig(
            llm_provider=LLMProvider.OPENAI,
            model_configs=default_model_configs,
            user_preferences=UserPreferences()
        )
        
        self.save_config(config)
        return config
    
    def _load_api_keys(self, config_data: Dict[str, Any]) -> None:
        """Load API keys from secure storage into config data."""
        model_configs = config_data.get('model_configs', {})
        
        for provider, config in model_configs.items():
            if isinstance(config, dict):
                stored_key = self.secure_storage.retrieve(f"{provider}_api_key")
                if stored_key:
                    config['api_key'] = stored_key
    
    def _save_api_keys(self, config_data: Dict[str, Any]) -> None:
        """Save API keys to secure storage and remove from config data."""
        model_configs = config_data.get('model_configs', {})
        
        for provider, config in model_configs.items():
            if isinstance(config, dict) and 'api_key' in config:
                api_key = config['api_key']
                if api_key and provider != 'ollama':  # Don't encrypt Ollama's dummy key
                    self.secure_storage.store(f"{provider}_api_key", api_key)
                    config['api_key'] = '[ENCRYPTED]'
    
    def _update_config_if_needed(self, config: AppConfig) -> None:
        """Update configuration with any new default values."""
        updated = False
        
        # Check if any providers are missing from model_configs
        for provider in LLMProvider:
            if provider not in config.model_configs:
                if provider == LLMProvider.GOOGLE:
                    config.model_configs[provider] = ModelConfig(
                        model="gemini-2.5-flash",
                        temperature=0.7,
                        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                    )
                elif provider == LLMProvider.OLLAMA:
                    config.model_configs[provider] = ModelConfig(
                        model="llama2",
                        api_key="ollama",
                        temperature=0.7,
                        base_url="http://localhost:11434/v1"
                    )
                else:  # OpenAI
                    config.model_configs[provider] = ModelConfig(
                        model="gpt-4",
                        temperature=0.7
                    )
                updated = True
        
        if updated:
            self.save_config(config)
    
    def update_provider(self, provider: LLMProvider) -> None:
        """
        Update the current LLM provider.
        
        Args:
            provider: The new LLM provider
            
        Raises:
            ConfigurationError: If provider update fails
        """
        try:
            config = self.config
            config.llm_provider = provider
            self.save_config(config)
            display_success(f"LLM provider updated to {provider.value}")
        except Exception as e:
            raise ConfigurationError(f"Failed to update provider: {e}")
    
    def update_model_config(self, provider: LLMProvider, model_config: ModelConfig) -> None:
        """
        Update model configuration for a provider.
        
        Args:
            provider: The LLM provider
            model_config: The new model configuration
            
        Raises:
            ConfigurationError: If model config update fails
        """
        try:
            # Validate the model configuration
            if model_config.api_key and provider != LLMProvider.OLLAMA:
                InputValidator.validate_api_key(model_config.api_key, provider.value)
            
            InputValidator.validate_model_name(model_config.model)
            InputValidator.validate_temperature(model_config.temperature)
            
            config = self.config
            config.model_configs[provider] = model_config
            self.save_config(config)
            
            display_success(f"Model configuration updated for {provider.value}")
            
        except ValidationError as e:
            raise ConfigurationError(f"Invalid model configuration: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to update model configuration: {e}")
    
    def set_api_key(self, provider: LLMProvider, api_key: str) -> None:
        """
        Set API key for a provider.
        
        Args:
            provider: The LLM provider
            api_key: The API key to set
            
        Raises:
            ConfigurationError: If API key setting fails
        """
        try:
            config = self.config
            
            # Get current model config or create new one
            if provider in config.model_configs:
                model_config = config.model_configs[provider]
            else:
                model_config = ModelConfig()
            
            # Update API key in both model config and secure storage
            model_config.api_key = api_key
            
            # Store in secure storage for retrieval
            self.secure_storage.store(f"{provider.value}_api_key", api_key)
            
            # Update configuration
            config.model_configs[provider] = model_config
            self.save_config(config)
            
            display_success(f"API key set for {provider.value}")
            
        except ValidationError as e:
            raise ConfigurationError(f"Invalid API key: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to set API key: {e}")
    
    def update_user_preferences(self, preferences: UserPreferences) -> None:
        """
        Update user preferences.
        
        Args:
            preferences: The new user preferences
            
        Raises:
            ConfigurationError: If preferences update fails
        """
        try:
            config = self.config
            config.user_preferences = preferences
            self.save_config(config)
            display_success("User preferences updated")
        except Exception as e:
            raise ConfigurationError(f"Failed to update user preferences: {e}")
    
    def get_current_model_config(self) -> ModelConfig:
        """
        Get the model configuration for the current provider.
        
        Returns:
            ModelConfig: Current model configuration
        """
        return self.config.get_current_model_config()
    
    def is_provider_configured(self, provider: LLMProvider) -> bool:
        """
        Check if a provider is properly configured.
        
        Args:
            provider: The LLM provider to check
            
        Returns:
            bool: True if configured, False otherwise
        """
        try:
            model_config = self.config.model_configs.get(provider)
            if not model_config:
                return False
            
            # Check if API key is required and present
            if provider != LLMProvider.OLLAMA:
                api_key = self.secure_storage.retrieve(f"{provider.value}_api_key")
                if not api_key:
                    return False
            
            return True
        except Exception:
            return False
    
    def list_configured_providers(self) -> list[LLMProvider]:
        """
        Get list of properly configured providers.
        
        Returns:
            List of configured providers
        """
        configured = []
        for provider in LLMProvider:
            if self.is_provider_configured(provider):
                configured.append(provider)
        return configured
    
    def export_config(self, file_path: str, include_keys: bool = False) -> None:
        """
        Export configuration to a file.
        
        Args:
            file_path: Path to export file
            include_keys: Whether to include API keys (not recommended)
            
        Raises:
            ConfigurationError: If export fails
        """
        try:
            config_data = self.config.dict()
            
            if not include_keys:
                # Remove API keys for security
                for provider_config in config_data['model_configs'].values():
                    if 'api_key' in provider_config:
                        provider_config['api_key'] = '[REDACTED]'
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            display_success(f"Configuration exported to {file_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to export configuration: {e}")
    
    def reset_config(self) -> None:
        """
        Reset configuration to defaults.
        
        Raises:
            ConfigurationError: If reset fails
        """
        try:
            # Clear secure storage
            for key in self.secure_storage.list_keys():
                self.secure_storage.delete(key)
            
            # Remove config file
            if self.config_file.exists():
                self.config_file.unlink()
            
            # Create new default config
            self._config = self._create_default_config()
            
            display_success("Configuration reset to defaults")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to reset configuration: {e}")
    
    def backup_config(self, backup_dir: str = None) -> str:
        """
        Create a backup of the current configuration.
        
        Args:
            backup_dir: Directory to store backup. If None, uses app data dir.
            
        Returns:
            str: Path to the backup file
            
        Raises:
            ConfigurationError: If backup fails
        """
        try:
            if backup_dir is None:
                backup_dir = self.app_dir / "backups"
            else:
                backup_dir = Path(backup_dir)
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = self.config.updated_at.strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"config_backup_{timestamp}.json"
            
            self.export_config(str(backup_file), include_keys=False)
            
            return str(backup_file)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to create configuration backup: {e}")


# Global configuration manager instance
config_manager = ConfigManager()
