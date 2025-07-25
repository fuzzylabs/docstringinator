# Docstringinator Pre-commit Setup

This document explains how to set up and use the docstringinator pre-commit hooks.

## Configuration

The docstringinator is configured to exclude directories starting with `.` and other common directories that shouldn't be processed:

### Excluded Patterns
- `*/tests/*` - Test files
- `*/migrations/*` - Database migrations
- `*/venv/*` - Virtual environments
- `*/.venv/*` - Virtual environments (alternative)
- `*/.git/*` - Git directory
- `*/.github/*` - GitHub workflows
- `*/.vscode/*` - VS Code settings
- `*/.idea/*` - PyCharm/IntelliJ settings
- `*/.pytest_cache/*` - Pytest cache
- `*/.mypy_cache/*` - MyPy cache
- `*/.ruff_cache/*` - Ruff cache
- `*/.coverage/*` - Coverage reports
- `*/.tox/*` - Tox environments
- `*/.eggs/*` - Python eggs
- `*/.eggs-info/*` - Egg info
- `*/__pycache__/*` - Python cache
- `*/build/*` - Build artifacts
- `*/dist/*` - Distribution files
- `*/node_modules/*` - Node.js modules
- `*/.*/*` - Any hidden directories

## Available Scripts

### 1. `run_docstringinator_precommit.py`
Processes all Python files in git diff (staged and unstaged changes).

**Usage:**
```bash
uv run python run_docstringinator_precommit.py
```

**Features:**
- Only processes files that have been modified in git
- Excludes hidden directories and common build artifacts
- Provides detailed output of what files are processed/excluded
- Returns appropriate exit codes for pre-commit integration

### 2. `run_docstringinator_files.py`
Processes specific files passed as command-line arguments.

**Usage:**
```bash
uv run python run_docstringinator_files.py file1.py file2.py
```

**Features:**
- Processes only the specified files
- Excludes files in hidden directories
- Useful for pre-commit hooks that pass filenames
- Efficient for processing only changed files

## Pre-commit Integration

The `.pre-commit-config.yaml` file includes a docstringinator hook that:

1. **Triggers on:** Python files (`types: [python]`)
2. **Runs:** `uv run python run_docstringinator_files.py`
3. **Passes filenames:** Yes (`pass_filenames: true`)
4. **Language:** System (uses uv)

### Installation

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Install the git hooks:
```bash
pre-commit install
```

3. Run on all files (optional):
```bash
pre-commit run --all-files
```

### Manual Usage

You can also run the scripts manually:

```bash
# Process git diff changes
uv run python run_docstringinator_precommit.py

# Process specific files
uv run python run_docstringinator_files.py path/to/file.py

# Process current directory (legacy)
uv run python run_docstringinator.py
```

## Configuration

The docstringinator uses `docstringinator.yaml` for configuration. Key settings:

- **LLM Provider:** Ollama with llama3.2:latest
- **Format Style:** Google docstring format
- **Exclusions:** Comprehensive list of directories to skip
- **Backup:** Creates backups before making changes

## Troubleshooting

### Ollama Not Running
If you get connection errors, ensure Ollama is running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### Model Not Available
If the configured model isn't available, update `docstringinator.yaml`:
```yaml
llm:
  model: "your-available-model"
```

### Excluding Additional Directories
Add patterns to the `exclude_patterns` list in `docstringinator.yaml` or update the exclusion logic in the scripts.

## Performance

- The scripts are optimized to only process relevant files
- Hidden directories are excluded to avoid processing system files
- Git diff integration ensures only changed files are processed
- Individual file processing provides better error reporting
