#!/bin/bash
# Pre-edit hook: Validate before file modifications

FILE_PATH="$1"

# Block edits to certain files
PROTECTED_FILES=("uv.lock" ".env" "secrets.json")

for protected in "${PROTECTED_FILES[@]}"; do
    if [[ "$FILE_PATH" == *"$protected"* ]]; then
        echo "ERROR: Cannot edit protected file: $protected"
        exit 1
    fi
done

# Ensure we're not editing in node_modules or .venv
if [[ "$FILE_PATH" == *"node_modules"* ]] || [[ "$FILE_PATH" == *".venv"* ]]; then
    echo "ERROR: Cannot edit files in node_modules or .venv"
    exit 1
fi

exit 0
