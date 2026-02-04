#!/bin/bash
# Post-edit hook: Run formatting and linting after file modifications

FILE_PATH="$1"

# Only process Python files
if [[ "$FILE_PATH" == *.py ]]; then
    # Run ruff format on the file
    if command -v uv &> /dev/null; then
        uv run ruff format "$FILE_PATH" 2>/dev/null || true
        uv run ruff check --fix "$FILE_PATH" 2>/dev/null || true
    fi
fi

exit 0
