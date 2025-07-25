"""Core Docstringinator functionality."""

import shutil
import time
from pathlib import Path
from typing import Any, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import load_config, validate_config
from .exceptions import ProcessingError
from .models import (
    BatchResult,
    Change,
    Config,
    DocstringInfo,
    LLMProvider,
    ProcessingResult,
)
from .parser import DocstringExtractor
from .providers import create_llm_provider


class Docstringinator:
    """Main class for processing docstrings using LLMs."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        llm_provider: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        """Initialise Docstringinator.

        Args:
            config_path: Path to configuration file.
            llm_provider: LLM provider to use.
            api_key: API key for the LLM provider.
            **kwargs: Additional configuration options.
        """
        self.console = Console()
        self.config = self._load_configuration(
            config_path,
            llm_provider,
            api_key,
            **kwargs,
        )
        self.llm_provider = create_llm_provider(
            self.config.llm.provider,
            self.config.llm.model_dump(),
        )
        self.extractor = DocstringExtractor()

    def _load_configuration(
        self,
        config_path: Optional[str],
        llm_provider: Optional[str],
        api_key: Optional[str],
        **kwargs: Any,
    ) -> Config:
        """Load and validate configuration.

        Args:
            config_path: Path to configuration file.
            llm_provider: LLM provider to use.
            api_key: API key for the LLM provider.
            **kwargs: Additional configuration options.

        Returns:
            Validated configuration object.
        """
        try:
            config = load_config(config_path)
        except Exception as e:
            self.console.print(f"[red]Failed to load configuration: {e}[/red]")
            raise

        # Override with provided arguments
        if llm_provider:
            config.llm.provider = LLMProvider(llm_provider)
        if api_key:
            config.llm.api_key = api_key

        # Apply additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        validate_config(config)
        return config

    def fix_file(self, file_path: str) -> ProcessingResult:
        """Fix docstrings in a single file.

        Args:
            file_path: Path to the Python file.

        Returns:
            Processing result with changes made.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        if not path.suffix == ".py":
            raise ValueError(f"Not a Python file: {file_path}")  # noqa: TRY003

        return self._process_file(path)

    def fix_directory(self, directory_path: str) -> BatchResult:
        """Process all Python files in a directory.

        Args:
            directory_path: Path to the directory.

        Returns:
            Batch processing result.
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(directory_path)

        if not directory.is_dir():
            raise NotADirectoryError(directory_path)

        return self._process_directory(directory)

    def fix_string(self, code: str) -> str:
        """Fix docstrings in a code string.

        Args:
            code: Python code as string.

        Returns:
            Code with fixed docstrings.
        """
        # This is a simplified version - in practice, you'd want to
        # parse the code, identify functions, generate docstrings,
        # and return the modified code
        functions = self.extractor.parser.parse_string(code)

        modified_code = code
        for func in functions:
            if not func.has_docstring:
                # Generate docstring for this function
                docstring = self._process_function(func, Path("temp.py"))
                if docstring:
                    # Insert docstring after function definition
                    # This is a simplified implementation
                    pass

        return modified_code

    def preview_changes(self, file_path: str) -> List[Change]:
        """Preview changes that would be made to a file.

        Args:
            file_path: Path to the Python file.

        Returns:
            List of changes that would be made.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        # Temporarily set dry_run to True
        return self._process_file(path).changes

    def _process_file(self, file_path: Path) -> ProcessingResult:
        """Process a single file.

        Args:
            file_path: Path to the file to process.

        Returns:
            Processing result with changes and statistics.
        """
        start_time = time.time()
        changes = []
        errors = []

        def _check_file_size(file_path: Path) -> None:
            """Check if file size is within limits."""
            file_size = file_path.stat().st_size
            if file_size > self.config.processing.max_file_size:
                raise ValueError(f"File too large: {file_path} bytes")  # noqa: TRY003

        try:
            # Check file size
            _check_file_size(file_path)

            # Create backup if needed
            if self.config.processing.backup_files:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)

            # Parse the file
            functions = self.extractor.extract_docstrings(file_path)

            # Filter functions that need docstrings
            target_functions = [
                func
                for func in functions
                if not func.has_docstring or self._should_improve_docstring(func)
            ]

            def _process_single_function(func: DocstringInfo) -> Optional[Change]:
                """Process a single function with error handling."""
                try:
                    return self._process_function(func, file_path)
                except (ValueError, RuntimeError) as e:
                    errors.append(f"Failed to process {func.function_name}: {e}")
                    return None
                except OSError as e:
                    errors.append(
                        f"System error processing {func.function_name}: {e}",
                    )
                    return None

            # Process each function
            for func in target_functions:
                change = _process_single_function(func)
                if change:
                    changes.append(change)

            # Apply changes if not in dry run mode
            if not self.config.processing.dry_run and changes:
                self._apply_changes(file_path, changes)

        except Exception as e:
            raise ProcessingError from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            file_path=file_path,
            changes=changes,
            errors=errors,
            warnings=[],
            success=len(errors) == 0,
            file_size=file_path.stat().st_size,
            processing_time=processing_time,
            docstrings_found=len(functions),
            docstrings_modified=len([c for c in changes if c.change_type == "modify"]),
            docstrings_added=len([c for c in changes if c.change_type == "add"]),
        )

    def _process_directory(self, directory: Path) -> BatchResult:
        """Process all Python files in a directory.

        Args:
            directory: Directory to process.

        Returns:
            Batch processing result.
        """
        start_time = time.time()
        results = []
        total_files = 0
        successful_files = 0
        failed_files = 0
        total_changes = 0
        total_errors = 0
        total_warnings = 0

        # Find all Python files
        python_files = list(directory.rglob("*.py"))

        # Filter files based on exclude/include patterns
        filtered_files = self._filter_files(python_files)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Processing files...", total=len(filtered_files))

            for file_path in filtered_files:
                try:
                    result = self._process_file(file_path)
                    results.append(result)
                    total_files += 1

                    if result.success:
                        successful_files += 1
                        total_changes += len(result.changes)
                    else:
                        failed_files += 1

                    total_errors += len(result.errors)
                    total_warnings += len(result.warnings)

                except (FileNotFoundError, ValueError) as e:
                    failed_files += 1
                    total_errors += 1
                    results.append(
                        ProcessingResult(
                            file_path=file_path,
                            errors=[f"Failed to process: {e}"],
                            success=False,
                            file_size=0,
                            processing_time=0,
                            docstrings_found=0,
                            docstrings_modified=0,
                            docstrings_added=0,
                        ),
                    )
                except OSError as e:
                    failed_files += 1
                    total_errors += 1
                    results.append(
                        ProcessingResult(
                            file_path=file_path,
                            errors=[f"Unexpected error: {e}"],
                            success=False,
                            file_size=0,
                            processing_time=0,
                            docstrings_found=0,
                            docstrings_modified=0,
                            docstrings_added=0,
                        ),
                    )

                progress.update(task, advance=1)

        total_processing_time = time.time() - start_time

        return BatchResult(
            total_files=total_files,
            successful_files=successful_files,
            failed_files=failed_files,
            total_changes=total_changes,
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_processing_time=total_processing_time,
            results=results,
        )

    def _filter_files(self, files: List[Path]) -> List[Path]:
        """Filter files based on include/exclude patterns.

        Args:
            files: List of file paths.

        Returns:
            Filtered list of files.
        """
        from pathspec import PathSpec
        from pathspec.patterns import GitWildMatchPattern

        # Create pathspec for exclude patterns
        exclude_spec = PathSpec.from_lines(
            GitWildMatchPattern,
            self.config.processing.exclude_patterns,
        )
        include_spec = PathSpec.from_lines(
            GitWildMatchPattern,
            self.config.processing.include_patterns,
        )

        filtered_files = []
        for file_path in files:
            # Convert to relative path for matching
            try:
                relative_path = file_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = file_path

            # Check if file should be excluded
            if exclude_spec.match_file(str(relative_path)):
                continue

            # Check if file should be included
            if include_spec.match_file(str(relative_path)):
                filtered_files.append(file_path)

        return filtered_files

    def _process_function(
        self,
        func: DocstringInfo,
        file_path: Path,
    ) -> Optional[Change]:
        """Process a single function.

        Args:
            func: Function information.
            file_path: Path to the file.

        Returns:
            Change object if docstring was modified, None otherwise.
        """
        try:
            # Generate new docstring
            response = self.llm_provider.generate_docstring(
                func,
                self.config.format.style,
            )

            new_docstring = self._clean_docstring(response.content)

            # Check if docstring needs to be added or improved
            if not func.has_docstring:
                return self._add_docstring(file_path, func, new_docstring)
            return self._improve_docstring(file_path, func, new_docstring)

        except OSError as e:
            if self.config.output.verbose:
                self.console.print(
                    f"[yellow]Warning: Failed to process {func.function_name}: {e}[/yellow]",
                )
            return None

    def _clean_docstring(self, docstring: str) -> str:
        """Clean and format docstring.

        Args:
            docstring: Raw docstring from LLM.

        Returns:
            Cleaned docstring.
        """
        try:
            # Remove triple quotes if present
            if (docstring.startswith('"""') and docstring.endswith('"""')) or (
                docstring.startswith("'''") and docstring.endswith("'''")
            ):
                docstring = docstring[3:-3]

            return docstring  # noqa: TRY300

        except OSError as e:
            if self.config.output.verbose:
                self.console.print(
                    f"[yellow]Warning: Failed to clean docstring: {e}[/yellow]",
                )
            return docstring

    def _add_docstring(
        self,
        file_path: Path,
        func: DocstringInfo,
        new_docstring: str,
    ) -> Optional[Change]:
        """Add a new docstring to a function.

        Args:
            file_path: Path to the file.
            func: Function information.
            new_docstring: New docstring to add.

        Returns:
            Change object or None if no change needed.
        """
        # This is a placeholder implementation
        # In a real implementation, you would modify the file
        return Change(
            file_path=file_path,
            line_number=func.line_number,
            original_text="",
            new_text=new_docstring,
            change_type="add",
            description=f"Add docstring to {func.function_name}",
        )

    def _improve_docstring(
        self,
        file_path: Path,
        func: DocstringInfo,
        new_docstring: str,
    ) -> Optional[Change]:
        """Improve an existing docstring.

        Args:
            file_path: Path to the file.
            func: Function information.
            new_docstring: New docstring to replace existing one.

        Returns:
            Change object or None if no change needed.
        """
        # This is a placeholder implementation
        # In a real implementation, you would modify the file
        return Change(
            file_path=file_path,
            line_number=func.line_number,
            original_text=func.existing_docstring or "",
            new_text=new_docstring,
            change_type="modify",
            description=f"Improve docstring for {func.function_name}",
        )

    def _should_improve_docstring(self, func: DocstringInfo) -> bool:
        """Check if a docstring should be improved.

        Args:
            func: Function information.

        Returns:
            True if docstring should be improved.
        """
        if not func.has_docstring or not func.existing_docstring:
            return False

        docstring = func.existing_docstring.strip()

        # Check if docstring is too short
        if len(docstring) < 20:
            return True

        # Check if docstring lacks key elements
        docstring_lower = docstring.lower()
        has_params = any(keyword in docstring_lower for keyword in ["param", "arg"])
        has_returns = "return" in docstring_lower

        # If function has parameters but docstring doesn't document them
        if func.parameters and not has_params:
            return True

        # If function has return type but docstring doesn't document it
        return bool(func.return_type and not has_returns)

    def _apply_changes(self, file_path: Path, changes: List[Change]) -> None:
        """Apply changes to a file.

        Args:
            file_path: Path to the file.
            changes: List of changes to apply.
        """
        # Read the file
        with file_path.open(encoding="utf-8") as f:
            lines = f.readlines()

        # Apply changes in reverse order to maintain line numbers
        for _change in sorted(changes, key=lambda x: x.line_number, reverse=True):
            # Insert docstring after function definition
            # This is a simplified implementation - in practice, you'd want
            # more sophisticated parsing to handle different function formats
            pass

        # Write the file
        with file_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)

    def print_results(self, result: ProcessingResult) -> None:
        """Print processing results.

        Args:
            result: Processing result to print.
        """
        if not self.config.output.verbose:
            return

        table = Table(title=f"Results for {result.file_path}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Success", str(result.success))
        table.add_row("Changes", str(len(result.changes)))
        table.add_row("Errors", str(len(result.errors)))
        table.add_row("Warnings", str(len(result.warnings)))
        table.add_row("Processing Time", f"{result.processing_time:.2f}s")
        table.add_row("File Size", f"{result.file_size} bytes")
        table.add_row("Docstrings Found", str(result.docstrings_found))
        table.add_row("Docstrings Modified", str(result.docstrings_modified))
        table.add_row("Docstrings Added", str(result.docstrings_added))

        self.console.print(table)

        if result.errors:
            self.console.print("\n[red]Errors:[/red]")
            for error in result.errors:
                self.console.print(f"  - {error}")

        if result.warnings:
            self.console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                self.console.print(f"  - {warning}")

    def print_batch_results(self, result: BatchResult) -> None:
        """Print batch processing results.

        Args:
            result: Batch result to print.
        """
        if not self.config.output.verbose:
            return

        table = Table(title="Batch Processing Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total Files", str(result.total_files))
        table.add_row("Successful", str(result.successful_files))
        table.add_row("Failed", str(result.failed_files))
        table.add_row("Total Changes", str(result.total_changes))
        table.add_row("Total Errors", str(result.total_errors))
        table.add_row("Total Warnings", str(result.total_warnings))
        table.add_row("Processing Time", f"{result.total_processing_time:.2f}s")

        self.console.print(table)

        if result.total_errors > 0:
            self.console.print("\n[red]Files with errors:[/red]")
            for file_result in result.results:
                if not file_result.success:
                    self.console.print(f"  - {file_result.file_path}")
                    for error in file_result.errors:
                        self.console.print(f"    - {error}")
