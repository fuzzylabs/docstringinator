"""Data models for Docstringinator."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocstringFormat(str, Enum):
    """Supported docstring formats."""

    GOOGLE = "google"
    NUMPY = "numpy"
    RESTRUCTUREDTEXT = "restructuredtext"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    OLLAMA = "ollama"


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider to use",
    )
    model: str = Field(default="gpt-4", description="Model name to use")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for generation",
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for generation",
    )
    timeout: int = Field(default=30, description="Timeout in seconds")


class FormatConfig(BaseModel):
    """Configuration for docstring formatting."""

    style: DocstringFormat = Field(
        default=DocstringFormat.GOOGLE,
        description="Docstring style",
    )
    include_examples: bool = Field(
        default=True,
        description="Include examples in docstrings",
    )
    include_type_hints: bool = Field(
        default=True,
        description="Include type hints in docstrings",
    )
    max_line_length: int = Field(default=88, description="Maximum line length")
    include_raises: bool = Field(default=True, description="Include raises section")
    include_returns: bool = Field(default=True, description="Include returns section")


class ProcessingConfig(BaseModel):
    """Configuration for processing options."""

    dry_run: bool = Field(default=False, description="Preview changes without applying")
    backup_files: bool = Field(
        default=True,
        description="Create backup files before modifying",
    )
    max_file_size: int = Field(
        default=1_000_000,
        description="Maximum file size in bytes",
    )
    exclude_patterns: List[str] = Field(
        default_factory=lambda: ["*/tests/*", "*/migrations/*", "*/venv/*"],
        description="Patterns to exclude from processing",
    )
    include_patterns: List[str] = Field(
        default_factory=lambda: ["*.py"],
        description="Patterns to include for processing",
    )


class OutputConfig(BaseModel):
    """Configuration for output options."""

    verbose: bool = Field(default=True, description="Enable verbose output")
    show_diff: bool = Field(default=True, description="Show diff of changes")
    create_backup: bool = Field(default=True, description="Create backup files")
    output_format: str = Field(
        default="text",
        description="Output format (text, json, yaml)",
    )


class Config(BaseModel):
    """Main configuration for Docstringinator."""

    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    format: FormatConfig = Field(
        default_factory=FormatConfig,
        description="Format configuration",
    )
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig,
        description="Processing configuration",
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output configuration",
    )

    class Config:
        """Pydantic configuration."""

        extra = "forbid"
        validate_assignment = True


class Change(BaseModel):
    """Represents a change to be made to a file."""

    file_path: Path = Field(description="Path to the file being changed")
    line_number: int = Field(description="Line number where the change occurs")
    original_text: str = Field(description="Original text")
    new_text: str = Field(description="New text")
    change_type: str = Field(description="Type of change (add, modify, remove)")
    description: str = Field(description="Description of the change")


class DocstringInfo(BaseModel):
    """Information about a docstring."""

    function_name: str = Field(description="Name of the function")
    class_name: Optional[str] = Field(
        default=None,
        description="Name of the class if method",
    )
    module_name: str = Field(description="Name of the module")
    signature: str = Field(description="Function signature")
    existing_docstring: Optional[str] = Field(
        default=None,
        description="Existing docstring if any",
    )
    line_number: int = Field(description="Line number where the function starts")
    end_line_number: int = Field(description="Line number where the function ends")
    has_docstring: bool = Field(
        description="Whether the function already has a docstring",
    )
    is_method: bool = Field(description="Whether this is a method (not a function)")
    is_async: bool = Field(description="Whether this is an async function")
    return_type: Optional[str] = Field(
        default=None,
        description="Return type annotation",
    )
    parameters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Function parameters",
    )


class ProcessingResult(BaseModel):
    """Result of processing a file."""

    file_path: Path = Field(description="Path to the processed file")
    changes: List[Change] = Field(
        default_factory=list,
        description="Changes made to the file",
    )
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings encountered",
    )
    success: bool = Field(description="Whether processing was successful")
    file_size: int = Field(description="Size of the file in bytes")
    processing_time: float = Field(
        description="Time taken to process the file in seconds",
    )
    docstrings_found: int = Field(description="Number of docstrings found")
    docstrings_modified: int = Field(description="Number of docstrings modified")
    docstrings_added: int = Field(description="Number of docstrings added")


class BatchResult(BaseModel):
    """Result of batch processing multiple files."""

    total_files: int = Field(description="Total number of files processed")
    successful_files: int = Field(description="Number of files processed successfully")
    failed_files: int = Field(description="Number of files that failed to process")
    total_changes: int = Field(description="Total number of changes made")
    total_errors: int = Field(description="Total number of errors encountered")
    total_warnings: int = Field(description="Total number of warnings encountered")
    total_processing_time: float = Field(description="Total processing time in seconds")
    results: List[ProcessingResult] = Field(
        default_factory=list,
        description="Individual file results",
    )
