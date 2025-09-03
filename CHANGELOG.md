# Changelog

All notable changes to the IELTS Practice CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-03

### Added
- Initial release of IELTS Practice CLI
- Support for Writing Task 2 practice and assessment
- Multi-provider AI integration (OpenAI, Google AI, Ollama)
- Structured JSON output for consistent assessment results
- Interactive CLI interface with rich formatting
- Session management and progress tracking
- Secure API key storage with encryption
- Comprehensive documentation and examples
- Statistics and progress analysis
- Export functionality for sessions and data
- Quick practice mode for offline use
- Live word count and time tracking during writing
- Detailed band score feedback following IELTS criteria

### Features
- **AI-Powered Assessment**: Intelligent evaluation using latest language models
- **Multiple Task Types**: Support for Writing Task 2 (Task 1 coming soon)
- **Real-time Feedback**: Live word count and time tracking
- **Progress Tracking**: Session history and improvement analytics
- **Secure Configuration**: Encrypted storage of API keys and settings
- **Rich CLI Interface**: Beautiful terminal output with organized results
- **Export Capabilities**: JSON export for sessions and statistics
- **Cross-platform Support**: Works on Windows, macOS, and Linux

### Provider Support
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo models
- **Google AI**: Gemini-2.5-flash, Gemini-1.5-pro, Gemini-1.5-flash models  
- **Ollama**: Local model support (llama2, llama3, mistral, phi3)

### Commands Available
- `practice` - Start new practice sessions
- `sessions` - Manage and view practice history
- `config` - Configure AI providers and preferences
- `stats` - View progress statistics and analytics
- `test` - Test AI provider connections

### Assessment Criteria
- Task Response/Achievement (25%)
- Coherence and Cohesion (25%)
- Lexical Resource (25%)
- Grammatical Range and Accuracy (25%)

### Documentation
- Complete user guide with step-by-step instructions
- Configuration guide for all AI providers
- Examples with sample responses and assessments
- Getting started guide for new users
- Contributing guidelines for developers

### Technical Features
- Async/await architecture for optimal performance
- SQLite database for local data storage
- Pydantic models for data validation
- Type hints throughout the codebase
- Comprehensive error handling and logging
- Cross-platform configuration directory management

### Fixes
- Resolved Gemini 2.5 Flash empty response issues
- Fixed JSON parsing with structured output implementation
- Improved error handling for API connection failures
- Enhanced token limit management for thinking models

---

## Future Releases

### [1.1.0] - Planned
- Writing Task 1 Academic support
- Writing Task 1 General Training support
- Enhanced statistics with visual charts
- Batch assessment capabilities
- Plugin system for custom assessments

### [1.2.0] - Planned
- Speaking practice modules (Parts 1, 2, 3)
- Voice recording and assessment
- Reading comprehension practice
- Listening practice with audio files

### [2.0.0] - Future
- Web interface for easier access
- Mobile app integration
- Teacher dashboard for classroom use
- Advanced analytics and reporting
- Multi-language support

---

## Version History

### Release Notes Format

Each release includes:
- **Added**: New features and capabilities
- **Changed**: Modifications to existing features
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes and issue resolutions
- **Security**: Security-related improvements

### Contributing to Changelog

When contributing to the project:
1. Add entries to the "Unreleased" section
2. Follow the established format
3. Include relevant details for users
4. Reference issue numbers when applicable

---

For detailed information about each release, see the [GitHub Releases](https://github.com/AIMLDev726/IELTSCLI/releases) page.
