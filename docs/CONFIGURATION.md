# Configuration Guide

This guide explains how to configure and customize the IELTS Practice CLI tool for your specific needs.

## Overview

The IELTS Practice CLI stores configuration in a JSON file located in your system's application data directory. The tool supports multiple AI providers and offers extensive customization options.

## Configuration File Location

**Windows:** `%APPDATA%\ieltscli\config.json`
**macOS:** `~/Library/Application Support/ieltscli/config.json`
**Linux:** `~/.local/share/ieltscli/config.json`

## AI Provider Configuration

### OpenAI Setup

OpenAI typically provides the highest quality assessments but requires a paid API key.

**Getting an OpenAI API Key:**
1. Visit https://platform.openai.com
2. Create an account or sign in
3. Go to "API Keys" section
4. Click "Create new secret key"
5. Copy the key (format: `sk-...`)

**Configuration:**
```bash
# Set OpenAI as provider
python main.py config --provider openai --api-key sk-your-openai-key-here

# Set specific model
python main.py config --provider openai --model gpt-4

# Test connection
python main.py test --connection
```

**Available Models:**
- `gpt-4` (recommended for best quality)
- `gpt-4-turbo` (faster, still high quality)
- `gpt-3.5-turbo` (more economical option)

### Google AI (Gemini) Setup

Google AI offers competitive assessment quality with generous free tier limits.

**Getting a Google AI API Key:**
1. Go to https://makersuite.google.com
2. Sign in with Google account
3. Click "Get API Key"
4. Create new API key
5. Copy the key

**Configuration:**
```bash
# Set Google AI as provider
python main.py config --provider google --api-key your-google-ai-key

# Set specific model
python main.py config --provider google --model gemini-2.5-flash

# Test connection
python main.py test --connection
```

**Available Models:**
- `gemini-2.5-flash` (latest, fastest)
- `gemini-1.5-pro` (balanced performance)
- `gemini-1.5-flash` (fast and efficient)

### Ollama (Local) Setup

Ollama runs AI models locally on your computer, requiring no API keys or internet connection for assessment.

**Installing Ollama:**
1. Download from https://ollama.ai
2. Install the application
3. Pull a model: `ollama pull llama2`

**Configuration:**
```bash
# Set Ollama as provider
python main.py config --provider ollama

# Set specific model
python main.py config --provider ollama --model llama2

# Test connection
python main.py test --connection
```

**Available Models:**
- `llama2` (general purpose, good for IELTS)
- `llama3` (improved version)
- `mistral` (alternative option)
- `phi3` (smaller, faster)

## User Preferences

### Default Settings

```bash
# Set default task type
python main.py config --set default_task_type --value writing_task_2

# Enable detailed feedback
python main.py config --set show_detailed_feedback --value true

# Enable session saving
python main.py config --set save_sessions --value true

# Set feedback language
python main.py config --set feedback_language --value en
```

### Writing Settings

```bash
# Enable word count warnings
python main.py config --set word_count_warnings --value true

# Set auto-submit timeout (minutes)
python main.py config --set auto_submit_timeout --value 60

# Set default time limits
python main.py config --set default_time_limit_task2 --value 40
python main.py config --set default_time_limit_task1 --value 20
```

### Assessment Settings

```bash
# Set assessment detail level
python main.py config --set assessment_detail --value detailed

# Enable progress tracking
python main.py config --set track_progress --value true

# Set minimum word count enforcement
python main.py config --set enforce_word_limits --value true
```

## Advanced Configuration

### Provider-Specific Settings

**OpenAI Advanced:**
```bash
# Set temperature for creativity
python main.py config --set openai_temperature --value 0.7

# Set custom base URL (for Azure OpenAI)
python main.py config --set openai_base_url --value https://your-resource.openai.azure.com

# Set organization ID
python main.py config --set openai_organization --value org-your-org-id
```

**Google AI Advanced:**
```bash
# Set temperature
python main.py config --set google_temperature --value 0.7

# Set safety settings
python main.py config --set google_safety_level --value medium
```

**Ollama Advanced:**
```bash
# Set custom Ollama URL
python main.py config --set ollama_base_url --value http://localhost:11434

# Set context window size
python main.py config --set ollama_context_size --value 4096
```

### Security Settings

```bash
# Enable API key encryption (default: true)
python main.py config --set encrypt_api_keys --value true

# Set encryption password (optional)
python main.py config --set encryption_password --value your-secure-password

# Enable secure deletion of temporary files
python main.py config --set secure_delete --value true
```

### Performance Settings

```bash
# Set request timeout (seconds)
python main.py config --set request_timeout --value 30

# Set retry attempts
python main.py config --set max_retries --value 3

# Enable response caching
python main.py config --set enable_caching --value true

# Set cache duration (hours)
python main.py config --set cache_duration --value 24
```

## Configuration Examples

### Student Setup (Balanced)

For students who want good quality assessment with reasonable costs:

```bash
# Use Google AI for cost-effectiveness
python main.py config --provider google --api-key your-google-key

# Enable detailed feedback
python main.py config --set show_detailed_feedback --value true

# Set reasonable time limits
python main.py config --set default_time_limit_task2 --value 40

# Enable progress tracking
python main.py config --set track_progress --value true
```

### Teacher Setup (Comprehensive)

For teachers who need detailed analysis:

```bash
# Use OpenAI for highest quality
python main.py config --provider openai --api-key your-openai-key
python main.py config --provider openai --model gpt-4

# Maximum detail level
python main.py config --set show_detailed_feedback --value true
python main.py config --set assessment_detail --value comprehensive

# Enable all tracking
python main.py config --set track_progress --value true
python main.py config --set save_sessions --value true
```

### Offline Setup (Local Only)

For users who prefer local processing:

```bash
# Use Ollama exclusively
python main.py config --provider ollama
python main.py config --provider ollama --model llama2

# Disable cloud features
python main.py config --set cloud_sync --value false

# Enable local caching
python main.py config --set enable_caching --value true
```

### Budget Setup (Minimal Cost)

For users who want to minimize API costs:

```bash
# Use the most economical model
python main.py config --provider openai --model gpt-3.5-turbo

# Reduce assessment frequency
python main.py config --set assessment_mode --value essential

# Use quick mode more often
python main.py config --set default_mode --value quick
```

## Backup and Migration

### Exporting Configuration

```bash
# Export current configuration
python main.py config --export my_config.json

# Export with user data
python main.py config --export-full complete_backup.json
```

### Importing Configuration

```bash
# Import configuration only
python main.py config --import my_config.json

# Import full backup
python main.py config --import-full complete_backup.json
```

### Migration Between Devices

1. **Export from old device:**
   ```bash
   python main.py config --export-full migration_backup.json
   python main.py sessions --export all_sessions.json
   ```

2. **Transfer files** to new device

3. **Import on new device:**
   ```bash
   python main.py config --import-full migration_backup.json
   python main.py sessions --import all_sessions.json
   ```

## Troubleshooting Configuration

### Common Issues

**Configuration Not Saving:**
```bash
# Check file permissions
python main.py config --check-permissions

# Reset to defaults
python main.py config --reset

# Manual file location check
python main.py config --show-path
```

**API Key Problems:**
```bash
# Test current key
python main.py test --connection

# Reset API key
python main.py config --provider PROVIDER --api-key NEW_KEY

# Clear stored keys
python main.py config --clear-keys
```

**Invalid Settings:**
```bash
# Validate configuration
python main.py config --validate

# Reset specific setting
python main.py config --reset-setting setting_name

# Show all settings
python main.py config --show-all
```

### Configuration Reset

**Complete Reset:**
```bash
python main.py config --reset-all
```

**Partial Reset:**
```bash
# Reset provider settings only
python main.py config --reset-providers

# Reset user preferences only
python main.py config --reset-preferences

# Reset security settings only
python main.py config --reset-security
```

## Environment Variables

You can also use environment variables for configuration:

```bash
# API keys
export IELTSCLI_OPENAI_API_KEY=sk-your-key
export IELTSCLI_GOOGLE_API_KEY=your-google-key

# Provider preference
export IELTSCLI_DEFAULT_PROVIDER=openai

# Model preference
export IELTSCLI_DEFAULT_MODEL=gpt-4

# Data directory
export IELTSCLI_DATA_DIR=/custom/path/to/data
```

Environment variables take precedence over configuration file settings.

## Configuration Schema

The configuration file follows this structure:

```json
{
    "llm_provider": "openai",
    "model_configs": {
        "openai": {
            "model": "gpt-4",
            "api_key": "[encrypted]",
            "base_url": null,
            "temperature": 0.7
        }
    },
    "user_preferences": {
        "default_task_type": "writing_task_2",
        "show_detailed_feedback": true,
        "save_sessions": true,
        "word_count_warnings": true,
        "feedback_language": "en"
    },
    "version": "1.0.0",
    "created_at": "2025-09-03T22:00:00",
    "updated_at": "2025-09-03T22:30:00"
}
```

This configuration system provides flexibility while maintaining security and ease of use. For additional help, use `python main.py config --help` or contact support.
