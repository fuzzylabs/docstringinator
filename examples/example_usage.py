"""Example usage of Docstringinator.

This file demonstrates how to use the Docstringinator library to fix docstrings
in Python code.
"""

import os
from pathlib import Path

from docstringinator import Docstringinator


def example_basic_usage():
    """Demonstrate basic usage of Docstringinator."""
    # Initialise Docstringinator with OpenAI
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Fix docstrings in a single file
    result = docstringinator.fix_file("path/to/your/file.py")
    print(f"Processed file: {result.success}")
    print(f"Changes made: {len(result.changes)}")

    # Process an entire directory
    result = docstringinator.fix_directory("path/to/your/project/")
    print(f"Total files processed: {result.total_files}")
    print(f"Successful: {result.successful_files}")
    print(f"Failed: {result.failed_files}")


def example_with_configuration():
    """Demonstrate usage with custom configuration."""
    # Create Docstringinator with custom configuration
    docstringinator = Docstringinator(
        config_path="docstringinator.yaml",
        llm_provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    # Preview changes without applying them
    changes = docstringinator.preview_changes("path/to/your/file.py")
    print(f"Would make {len(changes)} changes")

    # Apply changes
    result = docstringinator.fix_file("path/to/your/file.py")
    print(f"Successfully processed: {result.success}")


def example_batch_processing():
    """Demonstrate batch processing with progress tracking."""
    docstringinator = Docstringinator()

    # Process multiple files with detailed output
    result = docstringinator.fix_directory("path/to/your/project/")

    # Print detailed results
    docstringinator.print_batch_results(result)

    # Check for errors
    if result.failed_files > 0:
        print(f"Warning: {result.failed_files} files failed to process")
        for file_result in result.results:
            if not file_result.success:
                print(f"  - {file_result.file_path}: {file_result.errors}")


def example_custom_format():
    """Demonstrate usage with custom docstring format."""
    # Use NumPy style docstrings
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # The format is configured in the config file or can be set programmatically
    # For this example, we'll assume it's set to NumPy style in the config

    result = docstringinator.fix_file("path/to/your/file.py")
    print(f"Applied NumPy style docstrings: {result.success}")


def example_dry_run():
    """Demonstrate dry-run mode for previewing changes."""
    docstringinator = Docstringinator(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Preview changes without applying them
    changes = docstringinator.preview_changes("path/to/your/file.py")
    
    print("Preview of changes:")
    for change in changes:
        print(f"  - {change.description}")
        print(f"    Line {change.line_number}: {change.change_type}")
        print(f"    New text: {change.new_text[:100]}...")


def example_error_handling():
    """Demonstrate error handling."""
    try:
        docstringinator = Docstringinator(
            llm_provider="openai",
            api_key="invalid_key",  # This will cause an error
        )
        
        result = docstringinator.fix_file("path/to/your/file.py")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        # Handle the error appropriately


if __name__ == "__main__":
    # Run examples (uncomment the ones you want to test)
    
    # example_basic_usage()
    # example_with_configuration()
    # example_batch_processing()
    # example_custom_format()
    # example_dry_run()
    # example_error_handling()
    
    print("Docstringinator examples ready to run!")
    print("Uncomment the example functions you want to test.") 