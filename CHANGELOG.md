# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Core Docstringinator class for processing docstrings
- LLM integration with OpenAI and Anthropic providers
- Python code parser for extracting function information
- Configuration management with YAML support
- Command-line interface with Typer
- Rich console output with progress bars and tables
- Support for multiple docstring formats (Google, NumPy, reStructuredText)
- Batch processing of directories
- Dry-run mode for previewing changes
- Pre-commit hook integration
- Comprehensive test suite
- Documentation with Sphinx

### Planned
- Local LLM provider support (Ollama, etc.)
- More docstring format styles
- IDE integration plugins
- Web interface for configuration
- Performance optimisations
- Multi-language support

## [0.1.0] - 2024-01-01

### Added
- Initial release
- Basic docstring generation and improvement
- OpenAI and Anthropic LLM support
- Google, NumPy, and reStructuredText docstring formats
- Command-line interface
- Configuration file support
- Pre-commit hook integration 