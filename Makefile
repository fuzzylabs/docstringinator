.PHONY: help install install-dev test test-cov lint format clean build docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  docs         - Build documentation"
	@echo "  check        - Run all quality checks"
	@echo "  release      - Prepare for release"

# Install the package in development mode
install:
	uv sync

# Install development dependencies
install-dev:
	uv sync --group dev
	pre-commit install

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=docstringinator --cov-report=html --cov-report=term

# Run linting checks
lint:
	uv run ruff check docstringinator/
	uv run mypy docstringinator/
	uv run bandit -r docstringinator/
	uv run codespell docstringinator/

# Format code
format:
	uv run black docstringinator/
	uv run isort docstringinator/
	uv run ruff format docstringinator/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build the package
build: clean
	uv run python -m build

# Build wheel only
wheel: clean
	uv run python -m build --wheel

# Build source distribution
sdist: clean
	uv run python -m build --sdist

# Build documentation
docs:
	cd docs && make html

# Run all quality checks
check: lint test

# Prepare for release
release: clean build test lint

# Create a new virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # On Unix/macOS"
	@echo "  venv\\Scripts\\activate     # On Windows"

# Install pre-commit hooks
pre-commit-install:
	pre-commit install

# Run pre-commit on all files
pre-commit-all:
	pre-commit run --all-files

# Create default configuration
init-config:
	python -m docstringinator.cli init

# Show package info
info:
	python -m docstringinator.cli info

# Show version
version:
	python -m docstringinator.cli version 