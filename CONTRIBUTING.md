# Contributing to Docstringinator

Thank you for your interest in contributing to Docstringinator! This document provides guidelines and information for contributors.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate of others.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/docstringinator.git
   cd docstringinator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write your code following the style guidelines below
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=docstringinator

# Run specific test file
pytest tests/test_core.py
```

### 4. Code Quality Checks

```bash
# Format code
black docstringinator/
isort docstringinator/
ruff format docstringinator/

# Lint code
ruff check docstringinator/
mypy docstringinator/
codespell docstringinator/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

## Code Style Guidelines

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Use British English spelling in documentation and comments
- Maximum line length: 88 characters (enforced by Black)

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: add support for local LLM providers
fix: handle missing API keys gracefully
docs: update README with installation instructions
```

### Testing

- Write tests for all new functionality
- Aim for at least 80% code coverage
- Use descriptive test names
- Group related tests in test classes
- Use fixtures for common setup

### Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions and classes
- Update CHANGELOG.md for significant changes
- Keep documentation in sync with code changes

## Project Structure

```
docstringinator/
├── docstringinator/          # Main package
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── core.py              # Main functionality
│   ├── llm.py               # LLM provider integration
│   ├── models.py            # Data models
│   └── parser.py            # Python code parsing
├── tests/                   # Test suite
├── docs/                    # Documentation
├── README.md               # Project overview
├── CONTRIBUTING.md         # This file
├── CHANGELOG.md           # Version history
├── LICENSE                # MIT license
└── pyproject.toml         # Project configuration
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=docstringinator --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m slow

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (API calls, file system)
- Use fixtures for common setup
- Test edge cases and error conditions

Example test structure:

```python
import pytest
from docstringinator.core import Docstringinator


class TestDocstringinator:
    """Test the main Docstringinator class."""

    def test_initialisation(self):
        """Test that Docstringinator can be initialised."""
        docstringinator = Docstringinator()
        assert docstringinator is not None

    def test_fix_file_with_invalid_path(self):
        """Test that invalid file paths raise appropriate errors."""
        docstringinator = Docstringinator()

        with pytest.raises(FileNotFoundError):
            docstringinator.fix_file("nonexistent_file.py")
```

## Pull Request Guidelines

### Before Submitting

1. **Ensure all tests pass**
   ```bash
   pytest
   ```

2. **Run code quality checks**
   ```bash
   black docstringinator/
   isort docstringinator/
   ruff format docstringinator/
   ruff check docstringinator/
   mypy docstringinator/
   codespell docstringinator/
   ```

3. **Update documentation**
   - Update README.md if needed
   - Add docstrings for new functions
   - Update CHANGELOG.md

4. **Check your changes**
   ```bash
   git diff main
   ```

### Pull Request Template

When creating a pull request, please include:

- **Description**: What changes were made and why
- **Type of change**: Bug fix, feature, documentation, etc.
- **Testing**: How the changes were tested
- **Breaking changes**: Any breaking changes and migration steps
- **Related issues**: Links to related issues or discussions

## Release Process

### For Maintainers

1. **Update version**
   - Update version in `docstringinator/__init__.py`
   - Update version in `pyproject.toml`

2. **Update CHANGELOG.md**
   - Move unreleased changes to new version
   - Add release date

3. **Create release**
   - Create and push a new tag
   - Create GitHub release with changelog

4. **Publish to PyPI**
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and general discussion
- **Documentation**: Check the README and inline documentation

## License

By contributing to Docstringinator, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Docstringinator! 🚀
