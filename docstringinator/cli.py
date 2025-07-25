"""Command-line interface for Docstringinator."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import create_default_config
from .core import Docstringinator

app = typer.Typer(
    name="docstringinator",
    help="A Python tool for automatically fixing and improving docstrings using LLMs",
    add_completion=False,
)
console = Console()


def main(
    target: Optional[str] = typer.Argument(None, help="File or directory to process"),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to configuration file",
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="LLM provider (openai, anthropic, ollama)",
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="API key for LLM provider",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Preview changes without applying them",
    ),
    verbose: bool = typer.Option(True, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    format_style: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Docstring format style (google, numpy, restructuredtext)",
    ),
    temperature: Optional[float] = typer.Option(
        None, "--temperature", "-t", help="Temperature for LLM generation (0.0-2.0)",
    ),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model to use"),
) -> None:
    """Process Python files to add or improve docstrings.

    Examples:
        # Fix a single file
        docstringinator path/to/file.py

        # Process an entire directory
        docstringinator path/to/directory/

        # Preview changes without applying them
        docstringinator path/to/file.py --dry-run

        # Use custom configuration
        docstringinator path/to/file.py --config custom_config.yaml

        # Specify LLM provider and API key
        docstringinator path/to/file.py --provider openai --api-key your-key-here
    """
    try:
        # Set up configuration overrides
        config_overrides: Dict[str, Any] = {}
        if dry_run:
            config_overrides["processing"] = {"dry_run": True}
        if not verbose or quiet:
            config_overrides["output"] = {"verbose": False}
        if format_style:
            config_overrides["format"] = {"style": format_style}
        if temperature is not None:
            config_overrides["llm"] = {"temperature": temperature}
        if model:
            config_overrides["llm"] = {"model": model}

        # Check if target is provided
        if not target:
            console.print("[red]Error: No target file or directory specified[/red]")
            console.print("Use 'docstringinator --help' for usage information")
            sys.exit(1)

        # Initialise Docstringinator
        docstringinator = Docstringinator(
            config_path=config,
            llm_provider=provider,
            api_key=api_key,
            **config_overrides,
        )

        # Process the target
        target_path = Path(target)
        if not target_path.exists():
            console.print(f"[red]Error: Target '{target}' does not exist[/red]")
            sys.exit(1)

        if target_path.is_file():
            file_result = docstringinator.fix_file(str(target_path))
            docstringinator.print_results(file_result)

            if not file_result.success:
                console.print(f"[red]Failed to process {target_path}[/red]")
                sys.exit(1)
            elif file_result.changes:
                console.print(f"[green]Successfully processed {target_path}[/green]")
            else:
                console.print(f"[yellow]No changes needed for {target_path}[/yellow]")

        elif target_path.is_dir():
            batch_result = docstringinator.fix_directory(str(target_path))
            docstringinator.print_batch_results(batch_result)

            if batch_result.failed_files > 0:
                console.print(
                    f"[red]Failed to process {batch_result.failed_files} files[/red]",
                )
                sys.exit(1)
            elif batch_result.total_changes > 0:
                console.print(
                    f"[green]Successfully processed {batch_result.successful_files} files[/green]",
                )
            else:
                console.print("[yellow]No changes needed for any files[/yellow]")

        else:
            console.print(f"[red]Error: '{target}' is not a file or directory[/red]")
            sys.exit(1)

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except OSError as e:
        console.print(f"[red]System error: {e}[/red]")
        sys.exit(1)


@app.command()
def init(config_path: str = "docstringinator.yaml") -> None:
    """Create a default configuration file.

    Args:
        config_path: Path where to create the configuration file.
    """
    try:
        create_default_config(config_path)
        console.print(f"[green]Created configuration file: {config_path}[/green]")
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("1. Edit the configuration file to set your API key")
        console.print("2. Run docstringinator on your Python files")

    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error creating configuration file: {e}[/red]")
        sys.exit(1)
    except OSError as e:
        console.print(f"[red]System error creating configuration file: {e}[/red]")
        sys.exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    version_text = Text(f"Docstringinator v{__version__}", style="bold blue")
    console.print(Panel(version_text, title="Version", border_style="blue"))


@app.command()
def info() -> None:
    """Show information about Docstringinator."""
    from . import __author__, __email__, __version__

    info_text = f"""
    Docstringinator - A Python tool for automatically fixing and improving docstrings using LLMs

    Version: {__version__}
    Author: {__author__}
    Email: {__email__}

    Features:
    - Automatic docstring generation for functions, classes, and modules
    - Docstring improvement with better formatting and clarity
    - Pre-commit integration for automated quality control
    - Multiple LLM support (OpenAI, Anthropic, etc.)
    - Customisable formatting (Google, NumPy, reStructuredText)
    - Batch processing of entire directories
    - Dry-run mode to preview changes

    Usage:
    docstringinator <file_or_directory> [options]

    Examples:
    - docstringinator path/to/file.py
    - docstringinator path/to/directory/ --dry-run
    - docstringinator path/to/file.py --provider openai --api-key your-key
    """

    console.print(Panel(info_text, title="About Docstringinator", border_style="green"))


def main_wrapper() -> None:
    """Wrapper for the main function to handle exceptions gracefully."""
    try:
        app()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except OSError as e:
        console.print(f"\n[red]System error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main_wrapper()
