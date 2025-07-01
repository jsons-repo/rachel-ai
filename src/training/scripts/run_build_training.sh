#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then
  echo "❌ Usage: ./run_build_training.sh path/to/gpt_output.json"
  exit 1
fi

INPUT_PATH="$1"

# Optional: activate your virtual environment
# source /path/to/venv/bin/activate

echo "🧠 Generating training prompts from: $INPUT_PATH"

# Ensure we run from project root so PYTHONPATH=src works correctly
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Run the Python module with correct PYTHONPATH
PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.gpt_to_training "$INPUT_PATH"

echo "✅ Done generating training.json"
