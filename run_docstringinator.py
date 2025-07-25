#!/usr/bin/env python3
"""Script to run docstringinator with YAML config."""

import sys
from pathlib import Path

# Add the docstringinator package to the path
sys.path.insert(0, str(Path(__file__).parent))

from docstringinator.core import Docstringinator


def main() -> None:
    """
    Analyse the system and generate documentation for the run_docstringinator module.

    This function serves as the entry point for the application, initiating the analysis process and generating documentation accordingly.

    Args:
        None

    Returns:
        None

    Raises:
        SystemError: If an error occurs during the analysis process.

    Example:
        >>> main()
    """
    try:
        # Initialize docstringinator with the YAML config
        docstringinator = Docstringinator(config_path="docstringinator.yaml")

        # Process the current directory
        result = docstringinator.fix_directory(".")

        # Print results
        docstringinator.print_batch_results(result)

        if result.failed_files > 0:
            sys.exit(1)

    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
