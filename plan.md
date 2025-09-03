# IELTS CLI Application - Detailed Development Plan

## Project Overview

A comprehensive IELTS (International English Language Testing System) CLI application built with Python that provides interactive practice sessions, real-time feedback, and performance analytics using advanced LLM integration.

## Core Features

### 1. Interactive Practice Sessions
- Multi-line markdown-enabled input for user responses
- Rich CLI interface with proper markdown rendering
- Support for all IELTS task types (starting with Writing Task 2)
- Real-time response capture with special keyword submission

### 2. LLM Integration
- Unified OpenAI client with multiple provider support:
  - OpenAI (GPT models) - Default base URL
  - Google AI (Gemini) - Custom base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
  - Ollama (Local models) - Custom base URL: `http://localhost:11434/v1`
- Single OpenAI package for all providers
- Configurable model selection with suggested and custom model support
- User can enter any custom model name beyond predefined suggestions
- Async communication for optimal performance

### 3. IELTS Assessment Engine
- Comprehensive criteria-based analysis
- Band score calculation (1-9 scale)
- Detailed feedback on:
  - Task Achievement/Response
  - Coherence and Cohesion
  - Lexical Resource
  - Grammatical Range and Accuracy

### 4. Configuration Management
- Secure API key storage in `~/.ieltscli/`
- User preference management
- Model configuration persistence with custom model support
- Interactive model selection (suggested + custom models)
- One-time setup with CLI-based updates

### 5. Analytics & Progress Tracking
- Historical performance data
- Progress visualization
- Mistake pattern analysis
- Improvement recommendations

## Technical Architecture

### Technology Stack
- **Language**: Python 3.9+
- **Async Framework**: asyncio, aiohttp
- **CLI Framework**: Rich, Typer
- **Markdown Rendering**: Rich markdown support
- **Data Storage**: SQLite for local data, JSON for config
- **LLM Integration**: Async OpenAI package with custom base URLs for all providers

### Project Structure
```
IELTSCLI/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── commands.py         # CLI commands
│   │   ├── interface.py        # Rich UI components
│   │   └── input_handler.py    # Multi-line input handling
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── models.py           # Data models
│   │   └── session.py          # Practice session logic
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py           # Unified OpenAI client manager
│   │   └── providers.py        # Provider configurations
│   ├── assessment/
│   │   ├── __init__.py
│   │   ├── criteria.py         # IELTS criteria definitions
│   │   ├── analyzer.py         # Response analysis engine
│   │   └── scorer.py           # Band score calculation
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite operations
│   │   └── models.py           # Database models
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py          # Utility functions
│       └── validators.py       # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_cli/
│   ├── test_core/
│   ├── test_llm/
│   └── test_assessment/
├── docs/
│   ├── user_guide.md
│   ├── api_reference.md
│   └── ielts_criteria.md
├── requirements.txt
├── setup.py
├── README.md
└── .env.example
```

## Development Phases

### Phase 1: Foundation & Setup (Week 1)
1. **Project Initialization**
   - Set up project structure
   - Create virtual environment
   - Install core dependencies
   - Initialize git repository

2. **Configuration System**
   - Implement secure config storage
   - Create API key management
   - Build user preference system
   - Add configuration validation

3. **Basic CLI Framework**
   - Set up Rich CLI interface
   - Implement command structure
   - Create help system
   - Add basic navigation

### Phase 2: Core LLM Integration (Week 2)
1. **LLM Client Architecture**
   - Unified OpenAI client with provider configs
   - Custom base URL management
   - Implement async communication
   - Add error handling and retries
   - Create response parsing

2. **Provider Implementation**
   - OpenAI client with default base URL
   - Google AI with Gemini base URL
   - Ollama client with local base URL
   - Suggested model lists with custom model input support
   - Model validation and fallback mechanisms

3. **Testing & Validation**
   - Unit tests for unified client
   - Integration tests for all providers
   - Error scenario testing
   - Performance benchmarking

### Phase 3: IELTS Assessment Engine (Week 3)
1. **Criteria Definition**
   - Writing Task 2 criteria implementation
   - Band score descriptors
   - Assessment rubrics
   - Feedback templates

2. **Analysis Engine**
   - Response parsing and analysis
   - Criteria-based evaluation
   - Score calculation algorithms
   - Detailed feedback generation

3. **Quality Assurance**
   - Assessment accuracy testing
   - Feedback quality validation
   - Score consistency checks
   - Edge case handling

### Phase 4: Interactive Interface (Week 4)
1. **Input System**
   - Multi-line markdown input
   - Real-time rendering
   - Special keyword detection
   - Input validation

2. **Response Display**
   - Rich markdown rendering
   - Formatted feedback display
   - Score visualization
   - Progress indicators

3. **Session Management**
   - Practice session flow
   - State management
   - Session persistence
   - Recovery mechanisms

### Phase 5: Data Storage & Analytics (Week 5)
1. **Database Design**
   - SQLite schema design
   - Migration system
   - Data models
   - Query optimization

2. **Analytics Engine**
   - Performance tracking
   - Progress calculation
   - Trend analysis
   - Report generation

3. **Data Visualization**
   - Rich-based charts
   - Progress summaries
   - Improvement insights
   - Historical comparisons

### Phase 6: Advanced Features & Polish (Week 6)
1. **Enhanced CLI**
   - Advanced commands
   - Configuration management UI with model selection
   - Interactive model setup (suggested + custom)
   - Help and documentation
   - Error handling improvements

2. **Performance Optimization**
   - Async optimization
   - Caching strategies
   - Resource management
   - Response time improvements

3. **Documentation & Testing**
   - Comprehensive documentation
   - User guide creation
   - Final testing suite
   - Performance validation

## Key Implementation Details

### Unified LLM Client Architecture
```python
from openai import AsyncOpenAI
from typing import Dict, Any

class LLMClient:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.model = model
        
        # Configure base URL based on provider
        if provider == "openai":
            base_url = None  # Default OpenAI base URL
        elif provider == "google":
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif provider == "ollama":
            base_url = "http://localhost:11434/v1"
            api_key = "ollama"  # Required but unused for Ollama
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def analyze_response(self, prompt: str, response: str) -> dict:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": response}
        ]
        
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        return completion.choices[0].message.content
```

### Provider Configuration
```python
PROVIDER_CONFIGS = {
    "openai": {
        "base_url": None,
        "suggested_models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "requires_api_key": True,
        "allow_custom_models": True
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "suggested_models": ["gemini-2.5-flash", "gemini-pro", "gemini-1.5-pro"],
        "requires_api_key": True,
        "allow_custom_models": True
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "suggested_models": ["llama2", "llama3", "codellama", "mistral", "phi", "qwen"],
        "requires_api_key": False,
        "default_api_key": "ollama",
        "allow_custom_models": True
    }
}

class ModelSelector:
    @staticmethod
    def get_available_models(provider: str) -> dict:
        """Get suggested models and allow custom input"""
        config = PROVIDER_CONFIGS.get(provider, {})
        return {
            "suggested": config.get("suggested_models", []),
            "allow_custom": config.get("allow_custom_models", True),
            "custom_prompt": f"Enter custom model name for {provider} (or select from suggested):"
        }
    
    @staticmethod
    def validate_model(provider: str, model: str) -> bool:
        """Validate model name - always return True for custom models"""
        # For custom models, we'll let the LLM provider validate
        # during actual API calls
        return len(model.strip()) > 0
```

### Rich CLI Integration
```python
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def display_feedback(feedback: str):
    md = Markdown(feedback)
    panel = Panel(md, title="IELTS Feedback", border_style="blue")
    console.print(panel)

def select_model(provider: str) -> str:
    """Interactive model selection with suggested and custom options"""
    config = PROVIDER_CONFIGS.get(provider, {})
    suggested_models = config.get("suggested_models", [])
    
    # Display suggested models
    table = Table(title=f"Available Models for {provider.upper()}")
    table.add_column("Option", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("Description", style="green")
    
    for i, model in enumerate(suggested_models, 1):
        table.add_row(str(i), model, "Suggested model")
    
    table.add_row("C", "Custom", "Enter your own model name")
    console.print(table)
    
    choice = Prompt.ask(
        f"Select model for {provider}",
        choices=[str(i) for i in range(1, len(suggested_models) + 1)] + ["C", "c"],
        default="1"
    )
    
    if choice.lower() == "c":
        custom_model = Prompt.ask("Enter custom model name")
        console.print(f"[yellow]Using custom model: {custom_model}[/yellow]")
        return custom_model
    else:
        selected_model = suggested_models[int(choice) - 1]
        console.print(f"[green]Selected model: {selected_model}[/green]")
        return selected_model
```

### Configuration Management
```python
# ~/.ieltscli/config.json
{
    "llm_provider": "openai",
    "model_configs": {
        "openai": {
            "api_key": "encrypted_key",
            "model": "gpt-4",  // Can be any custom model name
            "temperature": 0.7,
            "is_custom_model": false
        },
        "google": {
            "api_key": "encrypted_key",
            "model": "gemini-2.5-flash",  // Or custom like "gemini-experimental-0801"
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "is_custom_model": false
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "model": "llama2",  // Or custom like "my-fine-tuned-model"
            "api_key": "ollama",
            "is_custom_model": false
        }
    },
    "user_preferences": {
        "default_task_type": "writing_task_2",
        "show_detailed_feedback": true,
        "save_sessions": true
    }
}
```

## IELTS Writing Task 2 Criteria

### Task Achievement (25%)
- Address all parts of the task
- Present a clear position throughout
- Support ideas with relevant examples
- Meet word count requirements (250+ words)

### Coherence and Cohesion (25%)
- Logical organization of information
- Clear progression throughout
- Appropriate use of cohesive devices
- Clear paragraphing

### Lexical Resource (25%)
- Range of vocabulary
- Accuracy of word choice
- Spelling accuracy
- Natural and appropriate usage

### Grammatical Range and Accuracy (25%)
- Range of sentence structures
- Accuracy of grammar
- Punctuation accuracy
- Error frequency and impact

## Success Metrics

### Technical Metrics
- Response time < 2 seconds for LLM calls
- 99.9% uptime for local operations
- Memory usage < 100MB
- Database query time < 100ms

### User Experience Metrics
- Setup completion rate > 95%
- Session completion rate > 90%
- User satisfaction score > 4.5/5
- Feature adoption rate > 80%

### Assessment Accuracy
- Correlation with human scores > 0.85
- Feedback relevance score > 4.0/5
- Improvement detection accuracy > 90%
- False positive rate < 5%

## Risk Mitigation

### Technical Risks
- **LLM API failures**: Implement robust retry logic and fallback mechanisms
- **Network connectivity**: Add offline mode for cached content
- **Performance issues**: Implement caching and optimization strategies
- **Data corruption**: Regular backups and data validation

### User Experience Risks
- **Complex setup**: Streamlined onboarding process
- **Poor feedback quality**: Continuous criteria refinement
- **Slow responses**: Async processing and progress indicators
- **Data privacy**: Local storage and encryption

## Testing Strategy

### Unit Tests
- Unified OpenAI client testing
- Provider configuration validation
- Mock LLM responses for all providers
- Configuration validation
- Database operations

### Integration Tests
- End-to-end session flow
- Unified LLM client with all providers
- CLI command testing
- Data persistence validation

### Performance Tests
- Load testing with multiple sessions
- Memory usage monitoring
- Response time benchmarking
- Concurrent operation testing

### User Acceptance Tests
- Real user scenario testing
- Feedback quality validation
- Usability testing
- Accessibility compliance

## CLI Command Examples

### Model Management Commands
```bash
# Initial setup with model selection
ieltscli setup

# Change LLM provider and select model
ieltscli config set-provider openai
ieltscli config select-model  # Shows suggested + custom option

# Set custom model directly
ieltscli config set-model "gpt-4-turbo-preview"  # Custom OpenAI model
ieltscli config set-model "gemini-experimental-0801"  # Custom Google model
ieltscli config set-model "my-fine-tuned-llama"  # Custom Ollama model

# View current configuration
ieltscli config show

# List available suggested models for current provider
ieltscli models list

# Test connection with current model
ieltscli test-connection
```

## Deployment & Distribution

### Package Distribution
- PyPI package publication
- Cross-platform compatibility
- Dependency management
- Version control strategy

### Installation Methods
- pip install ieltscli
- Standalone executables
- Docker containerization
- Development installation

### Documentation
- Comprehensive README
- API documentation
- User tutorials
- Troubleshooting guides

## Future Enhancements

### Additional IELTS Tasks
- Writing Task 1 (Academic/General)
- Speaking test simulation
- Reading comprehension
- Listening practice

### Advanced Features
- Voice input/output
- Real-time collaboration
- AI tutoring sessions
- Personalized study plans

### Platform Expansion
- Web interface
- Mobile applications
- API for third-party integration
- Cloud synchronization

## Timeline Summary

- **Week 1**: Foundation & Configuration
- **Week 2**: LLM Integration
- **Week 3**: Assessment Engine
- **Week 4**: Interactive Interface
- **Week 5**: Data & Analytics
- **Week 6**: Polish & Release

**Total Development Time**: 6 weeks
**Team Size**: 1-2 developers
**Estimated Effort**: 200-300 hours

## Conclusion

This plan provides a comprehensive roadmap for developing a professional-grade IELTS CLI application. The async architecture ensures optimal performance, while the rich CLI interface provides an excellent user experience. The modular design allows for easy maintenance and future enhancements.

The focus on IELTS Writing Task 2 as the initial implementation provides a solid foundation for expanding to other IELTS components. The integration of multiple LLM providers ensures flexibility and reliability, while the local storage approach maintains user privacy and data security.
