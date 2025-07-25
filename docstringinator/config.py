"""Configuration management for Docstringinator."""

from pathlib import Path
from typing import Optional

import requests
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import (
    APIKeyRequiredError,
    InvalidConfigurationError,
    InvalidFileSizeError,
    InvalidLineLengthError,
    InvalidTemperatureError,
    InvalidYAMLError,
    OllamaConnectionError,
)
from .models import Config, LLMProvider


class Settings(BaseSettings):
    """Settings for Docstringinator with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.1
    llm_timeout: int = 30
    ollama_base_url: str = "http://localhost:11434"

    # Processing Settings
    dry_run: bool = False
    backup_files: bool = True
    max_file_size: int = 1_000_000
    verbose: bool = True
    show_diff: bool = True

    # Format Settings
    docstring_style: str = "google"
    include_examples: bool = True
    include_type_hints: bool = True
    max_line_length: int = 88


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment variables.

    Args:
        config_path: Path to configuration file. If None, will look for
                    docstringinator.yaml in current directory.

    Returns:
        Configuration object.

    Raises:
        FileNotFoundError: If configuration file is not found.
        ValidationError: If configuration is invalid.
    """
    settings = Settings()

    # Try to load from YAML file
    if config_path is None:
        config_path = "docstringinator.yaml"

    config_file = Path(config_path)
    if config_file.exists():
        try:
            with config_file.open(encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidYAMLError(str(config_file)) from e

        # Merge with environment settings
        config_data = _merge_config_with_env(config_data, settings)
    else:
        # Use environment settings only
        config_data = _settings_to_config_dict(settings)

    try:
        return Config(**config_data)
    except Exception as e:
        raise InvalidConfigurationError(str(config_file)) from e


def _merge_config_with_env(config_data: dict, settings: Settings) -> dict:
    """Merge configuration file data with environment settings.

    Args:
        config_data: Configuration from file.
        settings: Settings from environment.

    Returns:
        Merged configuration dictionary.
    """
    # Ensure nested structure exists
    if "llm" not in config_data:
        config_data["llm"] = {}

    # Override with environment variables if not set in config
    if settings.openai_api_key and "api_key" not in config_data["llm"]:
        config_data["llm"]["api_key"] = settings.openai_api_key

    if settings.llm_provider and "provider" not in config_data["llm"]:
        config_data["llm"]["provider"] = settings.llm_provider

    if settings.llm_model and "model" not in config_data["llm"]:
        config_data["llm"]["model"] = settings.llm_model

    if settings.llm_temperature and "temperature" not in config_data["llm"]:
        config_data["llm"]["temperature"] = settings.llm_temperature

    if settings.llm_timeout and "timeout" not in config_data["llm"]:
        config_data["llm"]["timeout"] = settings.llm_timeout

    # Ollama-specific settings
    if settings.ollama_base_url and "base_url" not in config_data["llm"]:
        config_data["llm"]["base_url"] = settings.ollama_base_url

    # Processing settings
    if "processing" not in config_data:
        config_data["processing"] = {}

    if settings.dry_run and "dry_run" not in config_data["processing"]:
        config_data["processing"]["dry_run"] = settings.dry_run

    if settings.backup_files and "backup_files" not in config_data["processing"]:
        config_data["processing"]["backup_files"] = settings.backup_files

    if settings.max_file_size and "max_file_size" not in config_data["processing"]:
        config_data["processing"]["max_file_size"] = settings.max_file_size

    # Format settings
    if "format" not in config_data:
        config_data["format"] = {}

    if settings.docstring_style and "style" not in config_data["format"]:
        config_data["format"]["style"] = settings.docstring_style

    if settings.include_examples and "include_examples" not in config_data["format"]:
        config_data["format"]["include_examples"] = settings.include_examples

    if (
        settings.include_type_hints
        and "include_type_hints" not in config_data["format"]
    ):
        config_data["format"]["include_type_hints"] = settings.include_type_hints

    if settings.max_line_length and "max_line_length" not in config_data["format"]:
        config_data["format"]["max_line_length"] = settings.max_line_length

    # Output settings
    if "output" not in config_data:
        config_data["output"] = {}

    if settings.verbose and "verbose" not in config_data["output"]:
        config_data["output"]["verbose"] = settings.verbose

    if settings.show_diff and "show_diff" not in config_data["output"]:
        config_data["output"]["show_diff"] = settings.show_diff

    return config_data


def _settings_to_config_dict(settings: Settings) -> dict:
    """Convert settings to configuration dictionary.

    Args:
        settings: Settings object.

    Returns:
        Configuration dictionary.
    """
    return {
        "llm": {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "api_key": settings.openai_api_key or settings.anthropic_api_key,
            "temperature": settings.llm_temperature,
            "timeout": settings.llm_timeout,
        },
        "processing": {
            "dry_run": settings.dry_run,
            "backup_files": settings.backup_files,
            "max_file_size": settings.max_file_size,
        },
        "format": {
            "style": settings.docstring_style,
            "include_examples": settings.include_examples,
            "include_type_hints": settings.include_type_hints,
            "max_line_length": settings.max_line_length,
        },
        "output": {
            "verbose": settings.verbose,
            "show_diff": settings.show_diff,
        },
    }


def create_default_config(config_path: str = "docstringinator.yaml") -> None:
    """Create a default configuration file.

    Args:
        config_path: Path where to create the configuration file.
    """
    default_config = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "api_key": "${OPENAI_API_KEY}",
            "temperature": 0.1,
            "timeout": 30,
            # Ollama settings (uncomment to use Ollama)
            # "provider": "ollama",
            # "model": "llama2",
            # "base_url": "http://localhost:11434",
        },
        "format": {
            "style": "google",
            "include_examples": True,
            "include_type_hints": True,
            "max_line_length": 88,
            "include_raises": True,
            "include_returns": True,
        },
        "processing": {
            "dry_run": False,
            "backup_files": True,
            "max_file_size": 1_000_000,
            "exclude_patterns": [
                "*/tests/*",
                "*/migrations/*",
                "*/venv/*",
                "*/__pycache__/*",
                "*/build/*",
                "*/dist/*",
            ],
            "include_patterns": ["*.py"],
        },
        "output": {
            "verbose": True,
            "show_diff": True,
            "create_backup": True,
            "output_format": "text",
        },
    }

    config_file = Path(config_path)
    if not config_file.exists():
        with config_file.open("w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)


def validate_config(config: Config) -> None:
    """Validate configuration settings.

    Args:
        config: Configuration object to validate.

    Raises:
        ValueError: If configuration is invalid.
    """
    # Check API key for providers that require it
    if (
        config.llm.provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        and not config.llm.api_key
    ):
        raise APIKeyRequiredError(config.llm.provider)

    # Check Ollama connection if using Ollama provider
    if config.llm.provider == LLMProvider.OLLAMA:
        base_url = config.llm.model_dump().get(
            "ollama_base_url",
            "http://localhost:11434",
        )
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=3)
            response.raise_for_status()
        except requests.RequestException as e:
            raise OllamaConnectionError(base_url) from e

    # Check file size limit
    if config.processing.max_file_size <= 0:
        raise InvalidFileSizeError(config.processing.max_file_size)

    # Check temperature range
    if not 0.0 <= config.llm.temperature <= 2.0:
        raise InvalidTemperatureError(config.llm.temperature)

    # Check line length
    if config.format.max_line_length <= 0:
        raise InvalidLineLengthError(config.format.max_line_length)
