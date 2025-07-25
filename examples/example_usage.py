"""Example usage of Docstringinator.

This file demonstrates how to use the Docstringinator library to fix docstrings
in Python code.
"""

import logging
import os

from docstringinator import Docstringinator

# Configure logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage() -> None:
    """Demonstrate basic usage of Docstringinator."""
    # Initialise Docstringinator with OpenAI
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Fix docstrings in a single file
    result = docstringinator.fix_file("path/to/your/file.py")
    logger.info(f"Processed file: {result.success}")
    logger.info(f"Changes made: {len(result.changes)}")

    # Process multiple files individually
    files_to_process = [
        "path/to/your/file1.py",
        "path/to/your/file2.py",
        "path/to/your/file3.py",
    ]

    for file_path in files_to_process:
        try:
            result = docstringinator.fix_file(file_path)
            logger.info(f"Processed {file_path}: {result.success}")
            logger.info(f"Changes made: {len(result.changes)}")
        except (FileNotFoundError, ValueError, RuntimeError):  # noqa: PERF203
            logger.exception(f"Failed to process {file_path}")


def example_with_configuration() -> None:
    """Demonstrate usage with custom configuration."""
    # Create Docstringinator with custom configuration
    docstringinator = Docstringinator(
        config_path="docstringinator.yaml",
        llm_provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # Preview changes without applying them
    changes = docstringinator.preview_changes("path/to/your/file.py")
    logger.info(f"Would make {len(changes)} changes")

    # Apply changes
    result = docstringinator.fix_file("path/to/your/file.py")
    logger.info(f"Successfully processed: {result.success}")


def example_batch_processing() -> None:
    """Demonstrate batch processing with progress tracking."""
    docstringinator = Docstringinator()

    # Process multiple files individually with detailed output
    files_to_process = [
        "path/to/your/file1.py",
        "path/to/your/file2.py",
        "path/to/your/file3.py",
    ]

    successful_files = 0
    failed_files = 0
    total_changes = 0

    for file_path in files_to_process:
        try:
            result = docstringinator.fix_file(file_path)

            # Print detailed results for each file
            docstringinator.print_results(result)

            if result.success:
                successful_files += 1
                total_changes += len(result.changes)
                logger.info(f"✅ Successfully processed {file_path}")
            else:
                failed_files += 1
                logger.warning(f"❌ Failed to process {file_path}")

        except (FileNotFoundError, ValueError, RuntimeError):  # noqa: PERF203
            failed_files += 1
            logger.exception(f"❌ Error processing {file_path}")

    # Summary
    logger.info("📊 Batch processing complete:")
    logger.info(f"   Successful files: {successful_files}")
    logger.info(f"   Failed files: {failed_files}")
    logger.info(f"   Total changes: {total_changes}")


def example_custom_format() -> None:
    """Demonstrate usage with custom docstring format."""
    # Use NumPy style docstrings
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # The format is configured in the config file or can be set programmatically
    # For this example, we'll assume it's set to NumPy style in the config

    result = docstringinator.fix_file("path/to/your/file.py")
    logger.info(f"Applied NumPy style docstrings: {result.success}")


def example_dry_run() -> None:
    """Demonstrate dry-run mode for previewing changes."""
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Preview changes without applying them
    changes = docstringinator.preview_changes("path/to/your/file.py")

    logger.info("Preview of changes:")
    for change in changes:
        logger.info(f"  - {change.description}")
        logger.info(f"    Line {change.line_number}: {change.change_type}")
        logger.info(f"    New text: {change.new_text[:100]}...")


def example_error_handling() -> None:
    """Demonstrate error handling."""
    try:
        docstringinator = Docstringinator(
            llm_provider="openai",
            api_key="invalid_key",  # This will cause an error
        )

        docstringinator.fix_file("path/to/your/file.py")

    except (ValueError, RuntimeError):
        logger.exception("Error occurred")
        # Handle the error appropriately


if __name__ == "__main__":
    # Run examples (uncomment the ones you want to test)

    # example_basic_usage()
    # example_with_configuration()
    # example_batch_processing()
    # example_custom_format()
    # example_dry_run()
    # example_error_handling()

    logger.info("Docstringinator examples ready to run!")
    logger.info("Uncomment the example functions you want to test.")
