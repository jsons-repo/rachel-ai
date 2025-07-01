#!/bin/bash

set -e

# Usage: ./run_gpt.sh /path/to/whisper.json
INPUT_FILE="$1"

if [[ -z "$INPUT_FILE" ]]; then
  echo "❌ Error: No input file provided."
  echo "Usage: ./run_gpt.sh /path/to/whisper.json"
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "❌ Error: File not found at '$INPUT_FILE'"
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Running whisper_to_gpt on: $INPUT_FILE"
PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.whisper_to_gpt "$INPUT_FILE"

echo "✅ Done!"
