# Docstringinator

A Python tool for automatically fixing and improving docstrings using Large Language Models (LLMs). Designed to be used as a pre-commit hook to ensure consistent, high-quality documentation across your codebase.

## Features

- **Automatic docstring generation**: Generate docstrings for functions, classes, and modules that lack documentation
- **Docstring improvement**: Enhance existing docstrings with better formatting, examples, and clarity
- **Pre-commit integration**: Seamlessly integrate with pre-commit hooks for automated quality control
- **Multiple LLM support**: Configurable backend for different LLM providers (OpenAI, Anthropic, etc.)
- **Customisable formatting**: Support for various docstring formats (Google, NumPy, reStructuredText)
- **Batch processing**: Process entire directories or specific file patterns
- **Dry-run mode**: Preview changes without modifying files

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/docstringinator.git
cd docstringinator

# Install with uv
uv sync
```

### Using pip

```bash
pip install docstringinator
```

Or install from source:

```bash
git clone https://github.com/your-username/docstringinator.git
cd docstringinator
pip install -e .
```

## Quick Start

### Basic Usage

```python
from docstringinator import Docstringinator

# Initialise with your preferred LLM configuration
docstringinator = Docstringinator(
    llm_provider="openai",
    api_key="your-api-key-here"
)

# Fix docstrings in a single file
docstringinator.fix_file("path/to/your/file.py")

# Process an entire directory
docstringinator.fix_directory("path/to/your/project/")
```

### Pre-commit Integration

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: docstringinator
        name: Fix docstrings
        entry: docstringinator
        language: python
        types: [python]
        args: [--fix]
```

## Configuration

Create a `docstringinator.yaml` file in your project root:

```yaml
# LLM Configuration
llm:
  provider: openai  # or anthropic, ollama, etc.
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  temperature: 0.1
  # For Ollama:
  # provider: ollama
  # model: llama2
  # base_url: http://localhost:11434

# Docstring Format
format:
  style: google  # google, numpy, restructuredtext
  include_examples: true
  include_type_hints: true

# Processing Options
processing:
  dry_run: false
  backup_files: true
  max_file_size: 1000000  # bytes
  exclude_patterns:
    - "*/tests/*"
    - "*/migrations/*"
    - "*/venv/*"

# Output Options
output:
  verbose: true
  show_diff: true
  create_backup: true
```

### Using Ollama (Local Models)

To use Ollama for local model inference:

1. **Install Ollama**: Follow the [Ollama installation guide](https://ollama.ai/download)

2. **Pull a model**:
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama
   # or
   ollama pull mistral
   ```

3. **Configure for Ollama**:
   ```yaml
   llm:
     provider: "ollama"
     model: "llama2"
     base_url: "http://localhost:11434"  # Default Ollama URL
     temperature: 0.1
     timeout: 30
   ```

4. **Start Ollama**:
   ```bash
   ollama serve
   ```

5. **Run Docstringinator**:
   ```bash
   docstringinator fix file.py
   ```

   **Example configuration**: See `examples/ollama_config.yaml` for a complete Ollama configuration example.

## Command Line Interface

```bash
# Fix docstrings in a file
docstringinator fix path/to/file.py

# Process an entire directory
docstringinator fix path/to/directory/

# Dry run to preview changes
docstringinator fix path/to/file.py --dry-run

# Specify custom configuration
docstringinator fix path/to/file.py --config custom_config.yaml

# Show help
docstringinator --help
```

## Supported LLM Providers

- **OpenAI**: GPT-3.5, GPT-4, and other OpenAI models
- **Anthropic**: Claude models
- **Ollama**: Local models via Ollama (llama2, codellama, mistral, etc.)
- **Custom**: Implement your own LLM provider

## Docstring Formats

Docstringinator supports multiple docstring formats:

### Google Style
```python
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle in metres.

    Returns:
        The area of the circle in square metres.

    Raises:
        ValueError: If radius is negative.

    Example:
        >>> calculate_area(5.0)
        78.53981633974483
    """
```

### NumPy Style
```python
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Parameters
    ----------
    radius : float
        The radius of the circle in metres.

    Returns
    -------
    float
        The area of the circle in square metres.

    Raises
    ------
    ValueError
        If radius is negative.

    Examples
    --------
    >>> calculate_area(5.0)
    78.53981633974483
    """
```

## API Reference

### Docstringinator Class

The main class for processing docstrings.

```python
class Docstringinator:
    def __init__(
        self,
        llm_provider: str = "openai",
        config_path: Optional[str] = None,
        **kwargs
    ):
        """Initialise the Docstringinator.

        Args:
            llm_provider: The LLM provider to use.
            config_path: Path to configuration file.
            **kwargs: Additional configuration options.
        """
```

### Key Methods

- `fix_file(file_path: str) -> None`: Fix docstrings in a single file
- `fix_directory(directory_path: str) -> None`: Process all Python files in a directory
- `fix_string(code: str) -> str`: Fix docstrings in a code string
- `preview_changes(file_path: str) -> List[Change]`: Preview changes without applying them

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/docstringinator.git
cd docstringinator

# Install with uv (recommended)
uv sync --group dev
pre-commit install

# Or using pip
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
# Using uv (recommended)
uv run pytest

# Or using pip
pytest
```

### Code Quality

```bash
# Using uv (recommended)
uv run black docstringinator/
uv run isort docstringinator/
uv run ruff format docstringinator/
uv run ruff check docstringinator/
uv run mypy docstringinator/
uv run codespell docstringinator/

# Or using pip
black docstringinator/
isort docstringinator/
ruff format docstringinator/
ruff check docstringinator/
mypy docstringinator/
codespell docstringinator/
```

### Building the Package

```bash
# Build wheel only (recommended for distribution)
make wheel

# Build source distribution
make sdist

# Build both wheel and source distribution
make build

# Or using uv directly
uv run python -m build --wheel
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

- **Documentation**: [https://docstringinator.readthedocs.io](https://docstringinator.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/your-username/docstringinator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/docstringinator/discussions)

## Roadmap

- [x] Support for Ollama (local models)
- [ ] Support for more LLM providers
- [ ] Integration with popular IDEs
- [ ] Advanced docstring templates
- [ ] Multi-language support
- [ ] Performance optimisations
- [ ] Web interface for configuration
