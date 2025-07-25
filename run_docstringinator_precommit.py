# #!/usr/bin/env python3
# """Pre-commit script to run docstringinator on git diff changes only."""

# import subprocess
# import sys
# from pathlib import Path
# from typing import Set

# # Add the docstringinator package to the path
# sys.path.insert(0, str(Path(__file__).parent))

# from docstringinator.core import Docstringinator


# def get_git_diff_files() -> Set[str]:
#     """
#     Returns a set of file names that have been modified in the Git repository.

#     The function uses the Git command-line interface to retrieve the list of files with modifications.
#     The returned set contains the paths of these modified files, relative to the current working directory.

#     No parameters are required for this function as it relies on the default Git configuration and settings.

#     Returns:
#         A set of file names that have been modified in the Git repository.

#     Raises:
#         None

#     Example:
#         >>> get_git_diff_files()
#         {'file1.txt', 'file2.py'}
#     """
#     try:
#         # Get staged files
#         result = subprocess.run(
#             ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
#             capture_output=True,
#             text=True,
#             check=True,
#         )
#         staged_files = (
#             result.stdout.strip().split("\n") if result.stdout.strip() else []
#         )

#         # Get unstaged files
#         result = subprocess.run(
#             ["git", "diff", "--name-only", "--diff-filter=ACM"],
#             capture_output=True,
#             text=True,
#             check=True,
#         )
#         unstaged_files = (
#             result.stdout.strip().split("\n") if result.stdout.strip() else []
#         )

#         # Combine and filter for Python files
#         all_files = set(staged_files + unstaged_files)
#         python_files = {f for f in all_files if f.endswith(".py") and f}

#         return python_files
#     except subprocess.CalledProcessError:
#         print("Warning: Could not get git diff files. Processing all Python files.")
#         return set()


# def should_exclude_file(file_path: str) -> bool:
#     """
#     Determines whether a file should be excluded from analysis based on its path.

#     Args:
#         file_path (str, optional): The full path of the file to check. Defaults to None.

#     Returns:
#         bool: True if the file should be excluded, False otherwise.

#     Raises:
#         TypeError: If file_path is not a string.
#         ValueError: If file_path is an empty string.

#     Example:
#         >>> should_exclude_file('/path/to/excluded/file.txt')
#         True
#         >>> should_exclude_file(None)
#         False
#     """
#     exclude_patterns = [
#         "/tests/",
#         "/migrations/",
#         "/venv/",
#         "/.venv/",
#         "/.git/",
#         "/.github/",
#         "/.vscode/",
#         "/.idea/",
#         "/.pytest_cache/",
#         "/.mypy_cache/",
#         "/.ruff_cache/",
#         "/.coverage/",
#         "/.tox/",
#         "/.eggs/",
#         "/.eggs-info/",
#         "/__pycache__/",
#         "/build/",
#         "/dist/",
#         "/node_modules/",
#     ]

#     file_path_lower = file_path.lower()
#     return any(pattern in file_path_lower for pattern in exclude_patterns)


# def main() -> None:
#     """
#     Analyse and validate pre-commit hooks for a project.

#     This function serves as the entry point for the application, initiating the analysis of pre-commit hooks. It does not take any parameters and returns no value.

#     Raises:
#         SystemExit: If an error occurs during the analysis process.

#     Examples:
#         >>> main()
#         None
#     """
#     try:
#         # Initialize docstringinator with the YAML config
#         docstringinator = Docstringinator(config_path="docstringinator.yaml")

#         # Get git diff files
#         git_files = get_git_diff_files()

#         if not git_files:
#             return

#         # Filter out excluded files
#         files_to_process = [f for f in git_files if not should_exclude_file(f)]

#         if not files_to_process:
#             return

#         # Process each file individually
#         successful_files = 0
#         failed_files = 0

#         for file_path in files_to_process:
#             try:
#                 result = docstringinator.fix_file(file_path)

#                 if result.success:
#                     if result.changes:
#                         successful_files += 1
#                     else:
#                         pass
#                 else:
#                     failed_files += 1

#             except Exception:
#                 failed_files += 1

#         if failed_files > 0:
#             sys.exit(1)

#     except Exception:
#         import traceback

#         traceback.print_exc()
#         sys.exit(1)


# if __name__ == "__main__":
#     main()
