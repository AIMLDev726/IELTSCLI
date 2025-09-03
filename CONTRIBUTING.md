# Contributing to IELTS Practice CLI

We welcome contributions to improve the IELTS Practice CLI tool! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. **Check existing issues** first to avoid duplicates
2. **Create a new issue** with a clear title and description
3. **Include details** such as:
   - Your operating system
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

We love feature suggestions! When proposing new features:

1. **Explain the problem** the feature would solve
2. **Describe your proposed solution** in detail
3. **Consider alternatives** and mention any you've considered
4. **Think about backwards compatibility**

### Code Contributions

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/IELTSCLI.git
   cd IELTSCLI
   ```
3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

2. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

3. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

#### Making Changes

1. **Write clear, readable code** following Python best practices
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Follow the existing code style**
5. **Test your changes** thoroughly

#### Code Style Guidelines

- **Use Black** for code formatting: `black src/`
- **Follow PEP 8** for Python style guidelines
- **Use type hints** where appropriate
- **Write descriptive docstrings** for functions and classes
- **Keep functions focused** and reasonably sized
- **Use meaningful variable names**

#### Testing

- **Write unit tests** for new functions
- **Include integration tests** for major features
- **Test edge cases** and error conditions
- **Ensure all tests pass** before submitting

Run tests with:
```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_specific_file.py
```

#### Documentation

- **Update relevant documentation** in the `docs/` folder
- **Add docstrings** to new functions and classes
- **Update README.md** if adding new features
- **Include examples** for new functionality

### Pull Request Process

1. **Ensure your code passes all tests**
2. **Update documentation** as needed
3. **Create a pull request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - References to any related issues
   - Screenshots (if applicable)

4. **Be responsive** to feedback and questions
5. **Make requested changes** promptly

### Pull Request Template

When creating a pull request, please include:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or clearly documented)
```

## Development Guidelines

### Project Structure

Understanding the project structure helps when contributing:

```
IELTSCLI/
├── src/
│   ├── cli/                 # CLI interface components
│   ├── core/                # Core business logic
│   ├── llm/                 # AI provider integration
│   ├── assessment/          # IELTS scoring engine
│   ├── storage/             # Data management
│   └── utils/               # Helper functions
├── docs/                    # Documentation
├── tests/                   # Test files
└── main.py                  # Application entry point
```

### Key Areas for Contribution

**High Priority:**
- Bug fixes in core functionality
- Performance improvements
- Better error handling
- Additional AI provider support
- Test coverage improvements

**Medium Priority:**
- New IELTS task types (Speaking, Reading, Listening)
- Enhanced assessment features
- Better CLI user experience
- Documentation improvements

**Nice to Have:**
- Web interface
- Mobile app integration
- Advanced analytics
- Multi-language support

### Coding Conventions

#### Python Code Style

```python
# Good: Clear function names and type hints
def calculate_band_score(scores: List[float]) -> float:
    """Calculate overall IELTS band score from criterion scores.
    
    Args:
        scores: List of individual criterion scores
        
    Returns:
        Overall band score rounded to nearest 0.5
    """
    if not scores:
        return 0.0
    
    average = sum(scores) / len(scores)
    return round(average * 2) / 2

# Good: Clear class structure
class IELTSAssessment:
    """Represents an IELTS writing assessment."""
    
    def __init__(self, task_type: TaskType, scores: Dict[str, float]):
        self.task_type = task_type
        self.scores = scores
        self.overall_score = self._calculate_overall()
    
    def _calculate_overall(self) -> float:
        """Calculate overall score from individual criteria."""
        return calculate_band_score(list(self.scores.values()))
```

#### Error Handling

```python
# Good: Specific exception handling
try:
    response = await llm_client.assess_response(prompt, text)
except LLMConnectionError as e:
    logger.error(f"Failed to connect to LLM provider: {e}")
    raise SessionError("Assessment unavailable - connection failed")
except LLMAuthenticationError as e:
    logger.error(f"LLM authentication failed: {e}")
    raise SessionError("Assessment unavailable - check API key")
```

#### Async Code

```python
# Good: Proper async/await usage
async def process_assessment(session_id: str, user_response: str) -> Assessment:
    """Process user response and return assessment."""
    async with database.transaction():
        session = await database.get_session(session_id)
        
        if not session:
            raise SessionNotFoundError(f"Session {session_id} not found")
        
        assessment = await llm_client.assess_response(
            session.prompt, user_response
        )
        
        await database.save_assessment(session_id, assessment)
        return assessment
```

### Security Considerations

When contributing, keep security in mind:

- **Never commit API keys** or sensitive data
- **Use proper encryption** for stored credentials
- **Validate user inputs** to prevent injection attacks
- **Follow secure coding practices**
- **Review dependencies** for security issues

### Performance Guidelines

- **Use async/await** for I/O operations
- **Implement proper caching** where appropriate
- **Avoid blocking operations** in the main thread
- **Profile performance** for new features
- **Consider memory usage** for large datasets

## Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive in all interactions
- **Provide constructive feedback** during code reviews
- **Help newcomers** get started with contributing
- **Focus on the code**, not the person
- **Assume good intentions** from other contributors

### Communication

- **Use clear, descriptive commit messages**
- **Comment your code** where necessary
- **Ask questions** if anything is unclear
- **Share knowledge** with other contributors
- **Document your decisions** and reasoning

## Recognition

Contributors will be recognized in:
- The project's README.md file
- Release notes for significant contributions
- GitHub's contributor statistics

## Questions?

If you have questions about contributing:

1. **Check the documentation** in the `docs/` folder
2. **Search existing issues** for similar questions
3. **Create a new issue** with the "question" label
4. **Contact the maintainers** at aistudentlearn4@gmail.com

Thank you for contributing to IELTS Practice CLI! Your help makes this tool better for IELTS students worldwide. 🎯
