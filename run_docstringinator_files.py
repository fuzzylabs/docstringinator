#!/usr/bin/env python3
"""Script to run docstringinator on specific files passed as arguments."""

import sys
from pathlib import Path

# Add the docstringinator package to the path
sys.path.insert(0, str(Path(__file__).parent))

from docstringinator.core import Docstringinator


def should_exclude_file(file_path: str) -> bool:
    """
    Determines whether a file should be excluded from analysis based on its path.

    Args:
        file_path (str, optional): The full path of the file to check. Defaults to None.

    Returns:
        bool: True if the file should be excluded, False otherwise.

    Raises:
        TypeError: If file_path is not a string.

    Example:
        >>> should_exclude_file('/path/to/excluded/file.txt')
        True
        >>> should_exclude_file(None)
        False
    """
    exclude_patterns = [
        "/tests/",
        "/migrations/",
        "/venv/",
        "/.venv/",
        "/.git/",
        "/.github/",
        "/.vscode/",
        "/.idea/",
        "/.pytest_cache/",
        "/.mypy_cache/",
        "/.ruff_cache/",
        "/.coverage/",
        "/.tox/",
        "/.eggs/",
        "/.eggs-info/",
        "/__pycache__/",
        "/build/",
        "/dist/",
        "/node_modules/",
    ]

    file_path_lower = file_path.lower()
    return any(pattern in file_path_lower for pattern in exclude_patterns)


def main() -> None:
    """
    Analyse and process files within the specified directory.

    This function serves as the entry point for the application, responsible for initiating the file analysis process. It does not accept any parameters and returns no value.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If the script lacks permission to access the directory or its contents.

    Example:
        >>> main()
    """
    if len(sys.argv) < 2:
        sys.exit(1)

    try:
        # Initialize docstringinator with the YAML config
        docstringinator = Docstringinator(config_path="docstringinator.yaml")

        # Get files from command line arguments
        files = sys.argv[1:]

        # Filter Python files and exclude hidden directories
        python_files = [f for f in files if f.endswith(".py")]
        files_to_process = [f for f in python_files if not should_exclude_file(f)]

        if not files_to_process:
            return

        # Process each file individually
        successful_files = 0
        failed_files = 0

        for file_path in files_to_process:
            try:
                result = docstringinator.fix_file(file_path)

                if result.success:
                    if result.changes:
                        successful_files += 1
                    else:
                        pass
                else:
                    failed_files += 1

            except Exception:
                failed_files += 1

        if failed_files > 0:
            sys.exit(1)

    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
