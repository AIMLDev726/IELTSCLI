# User Guide - IELTS Practice CLI

This comprehensive guide covers all features and advanced usage of the IELTS Practice CLI tool.

## Table of Contents

1. [Core Commands](#core-commands)
2. [Practice Sessions](#practice-sessions)
3. [Assessment System](#assessment-system)
4. [Session Management](#session-management)
5. [Configuration Options](#configuration-options)
6. [Statistics and Progress](#statistics-and-progress)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## Core Commands

### Practice Command

The main command for starting IELTS practice sessions.

```bash
python main.py practice [OPTIONS]
```

**Options:**
- `--type TEXT`: Specify task type (writing_task_2, writing_task_1_academic, writing_task_1_general)
- `--time INTEGER`: Set time limit in minutes (default: 40 for Task 2, 20 for Task 1)
- `--quick`: Start quick practice without AI assessment
- `--resume TEXT`: Resume a specific session by ID
- `--custom-prompt TEXT`: Use your own prompt instead of generated one

**Examples:**
```bash
# Standard Writing Task 2 practice
python main.py practice --type writing_task_2

# 30-minute timed practice
python main.py practice --type writing_task_2 --time 30

# Quick practice without assessment
python main.py practice --quick

# Resume previous session
python main.py practice --resume a1b2c3d4-e5f6-1234-5678-90abcdef1234

# Custom prompt practice
python main.py practice --custom-prompt "Discuss the impact of social media on education"
```

### Sessions Command

Manage and view your practice sessions.

```bash
python main.py sessions [OPTIONS]
```

**Options:**
- `--all`: Show all sessions (default shows last 10)
- `--details TEXT`: Show detailed information for specific session
- `--delete TEXT`: Delete a specific session
- `--export TEXT`: Export sessions to JSON file
- `--filter TEXT`: Filter by task type or date range

**Examples:**
```bash
# View recent sessions
python main.py sessions

# View all sessions
python main.py sessions --all

# Session details
python main.py sessions --details SESSION_ID

# Export data
python main.py sessions --export my_sessions.json

# Filter by task type
python main.py sessions --filter writing_task_2

# Delete session
python main.py sessions --delete SESSION_ID
```

### Config Command

Configure application settings and AI providers.

```bash
python main.py config [OPTIONS]
```

**Options:**
- `--show`: Display current configuration
- `--provider TEXT`: Set AI provider (openai, google, ollama)
- `--api-key TEXT`: Set API key for the provider
- `--model TEXT`: Set specific model name
- `--set TEXT`: Set configuration value
- `--value TEXT`: Value to set (used with --set)

**Examples:**
```bash
# View configuration
python main.py config --show

# Set OpenAI provider
python main.py config --provider openai --api-key sk-your-key-here

# Set Google AI provider
python main.py config --provider google --api-key your-google-key

# Set Ollama (local)
python main.py config --provider ollama

# Set specific model
python main.py config --provider openai --model gpt-4-turbo

# Set preferences
python main.py config --set default_task_type --value writing_task_2
python main.py config --set show_detailed_feedback --value true
python main.py config --set word_count_warnings --value true
```

### Stats Command

View practice statistics and progress tracking.

```bash
python main.py stats [OPTIONS]
```

**Options:**
- `--detailed`: Show detailed statistics with charts
- `--period TEXT`: Filter by time period (week, month, year, all)
- `--export TEXT`: Export statistics to file
- `--task-type TEXT`: Filter by specific task type

**Examples:**
```bash
# Basic statistics
python main.py stats

# Detailed stats with charts
python main.py stats --detailed

# Monthly progress
python main.py stats --period month

# Export statistics
python main.py stats --export progress_report.json

# Task-specific stats
python main.py stats --task-type writing_task_2
```

### Test Command

Test system connectivity and configuration.

```bash
python main.py test [OPTIONS]
```

**Options:**
- `--connection`: Test AI provider connection
- `--all`: Test all configured providers
- `--database`: Test database connectivity

**Examples:**
```bash
# Test current provider
python main.py test --connection

# Test all providers
python main.py test --all

# Test database
python main.py test --database
```

## Practice Sessions

### Session Lifecycle

1. **Initialization**: Session created with unique ID
2. **Prompt Generation**: AI generates appropriate IELTS prompt
3. **Writing Phase**: User writes response with live feedback
4. **Submission**: User submits response for assessment
5. **Assessment**: AI evaluates response against IELTS criteria
6. **Results**: Detailed feedback and band scores provided
7. **Storage**: Session saved to database for future reference

### Writing Interface

When you start a practice session, you'll see:

```
📋 Task Prompt:
[Generated IELTS prompt appears here]

Your response:
[Type your essay here]

📊 Live Feedback:
Words: 156 / 250 | Time: 12:34 | Target: 27:26 remaining
```

### Submission Methods

- **Type `SUBMIT`** on a new line
- **Type `CANCEL`** to quit without saving
- **Ctrl+D** (Unix/Mac) or **Ctrl+Z** (Windows) to submit
- **Time expires** (auto-submit with warning)

### Quick Mode

Quick mode allows practice without AI assessment:
- Faster session startup
- No API calls or costs
- Basic word count and timing
- Good for focused writing practice
- Can be assessed later if needed

## Assessment System

### IELTS Criteria

**Writing Task 2:**
1. **Task Response (25%)**
   - Position and development of arguments
   - Relevance to the prompt
   - Examples and support

2. **Coherence and Cohesion (25%)**
   - Logical organization
   - Paragraph structure
   - Linking devices

3. **Lexical Resource (25%)**
   - Vocabulary range and accuracy
   - Word choice appropriateness
   - Spelling

4. **Grammatical Range and Accuracy (25%)**
   - Sentence variety
   - Grammar accuracy
   - Punctuation

**Writing Task 1:**
- Task Achievement (instead of Task Response)
- Other criteria remain the same

### Band Score Scale

- **9.0**: Expert user
- **8.0-8.5**: Very good user
- **7.0-7.5**: Good user
- **6.0-6.5**: Competent user
- **5.0-5.5**: Modest user
- **4.0-4.5**: Limited user

### Assessment Features

- **Structured JSON output** ensures consistent scoring
- **Criterion-specific feedback** with strengths and improvements
- **Overall feedback** with general observations
- **Actionable recommendations** for improvement
- **Comparative analysis** against previous sessions

## Session Management

### Session Data Structure

Each session contains:
- **Metadata**: ID, timestamps, task type, duration
- **Content**: Original prompt, user response, word count
- **Assessment**: Band scores, detailed feedback, recommendations
- **Progress**: Comparison with previous sessions

### Data Storage

- **Local SQLite database** for session history
- **Encrypted API keys** for security
- **JSON export** for backup and analysis
- **Cross-platform** data directory structure

### Session Operations

**Viewing Sessions:**
```bash
# Quick overview
python main.py sessions

# Detailed view
python main.py sessions --details SESSION_ID
```

**Exporting Data:**
```bash
# All sessions
python main.py sessions --export complete_history.json

# Filtered export
python main.py sessions --filter writing_task_2 --export task2_only.json
```

**Deleting Sessions:**
```bash
# Single session
python main.py sessions --delete SESSION_ID

# Multiple sessions (interactive)
python main.py sessions --cleanup
```

## Configuration Options

### Provider Settings

**OpenAI Configuration:**
```bash
python main.py config --provider openai --api-key sk-your-key
python main.py config --provider openai --model gpt-4-turbo
```

**Google AI Configuration:**
```bash
python main.py config --provider google --api-key your-google-key
python main.py config --provider google --model gemini-2.5-flash
```

**Ollama Configuration:**
```bash
python main.py config --provider ollama
python main.py config --provider ollama --model llama2
```

### User Preferences

```bash
# Default task type
python main.py config --set default_task_type --value writing_task_2

# Feedback settings
python main.py config --set show_detailed_feedback --value true
python main.py config --set feedback_language --value en

# Session settings
python main.py config --set save_sessions --value true
python main.py config --set auto_submit_timeout --value 60

# Word count warnings
python main.py config --set word_count_warnings --value true
```

### Configuration File

Configuration is stored in:
- **Windows**: `%APPDATA%/ieltscli/config.json`
- **macOS**: `~/Library/Application Support/ieltscli/config.json`
- **Linux**: `~/.local/share/ieltscli/config.json`

## Statistics and Progress

### Available Metrics

- **Overall Progress**: Average scores over time
- **Criterion Breakdown**: Performance by assessment area
- **Task Type Analysis**: Comparison across different tasks
- **Time Analysis**: Practice duration and efficiency
- **Improvement Trends**: Score progression tracking

### Statistical Views

**Summary Statistics:**
```bash
python main.py stats
```
Shows:
- Total sessions
- Average band score
- Recent trend
- Best performance

**Detailed Analysis:**
```bash
python main.py stats --detailed
```
Shows:
- Criterion-specific trends
- Time period comparisons
- Improvement suggestions
- Performance charts

**Time-based Analysis:**
```bash
python main.py stats --period month
python main.py stats --period week
python main.py stats --period year
```

### Progress Tracking

- **Session-to-session** comparison
- **Moving averages** for trend analysis
- **Goal setting** and achievement tracking
- **Weakness identification** for focused practice

## Advanced Features

### Custom Prompts

Use your own prompts for specific practice:
```bash
python main.py practice --custom-prompt "Discuss the advantages and disadvantages of remote work"
```

### Batch Operations

Process multiple sessions:
```bash
# Export all Writing Task 2 sessions
python main.py sessions --filter writing_task_2 --export task2_analysis.json

# Generate progress report
python main.py stats --detailed --export monthly_report.json
```

### API Integration

For developers wanting to integrate:
```python
from src.core.session import SessionManager
from src.llm.client import LLMClient

# Create session
session_manager = SessionManager()
session = await session_manager.create_session("writing_task_2")

# Assess response
assessment = await session_manager.assess_response(session_id, user_response)
```

### Database Operations

Advanced database management:
```bash
# Database info
python main.py maintenance --info

# Vacuum database
python main.py maintenance --vacuum

# Backup database
python main.py maintenance --backup backup_file.db

# Restore from backup
python main.py maintenance --restore backup_file.db
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
pip install -r requirements.txt
```

**API Connection Problems:**
```bash
python main.py test --connection
python main.py config --provider PROVIDER --api-key NEW_KEY
```

**Database Issues:**
```bash
python main.py maintenance --info
python main.py maintenance --vacuum
```

**Permission Errors:**
- Run as administrator (Windows)
- Check file permissions
- Ensure write access to app data directory

### Debugging

Enable verbose logging:
```bash
python main.py --verbose practice --type writing_task_2
```

Check configuration:
```bash
python main.py config --show
python main.py test --all
```

### Getting Help

**Command Help:**
```bash
python main.py --help
python main.py COMMAND --help
```

**System Information:**
```bash
python main.py --version
python main.py maintenance --info
```

**Support:**
- Email: aistudentlearn4@gmail.com
- GitHub: https://github.com/AIMLDev726/IELTSCLI/issues
- Documentation: Check `docs/` folder

This guide covers the main features of the IELTS Practice CLI. For specific examples and use cases, see the [Examples Documentation](EXAMPLES.md).
