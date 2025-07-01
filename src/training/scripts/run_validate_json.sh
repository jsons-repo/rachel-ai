#!/bin/bash
set -e

# Usage: ./run_validate_json.sh /path/to/transcript.json
INPUT_FILE="$1"

if [[ -z "$INPUT_FILE" ]]; then
  echo "❌ Error: No input file provided."
  echo "Usage: ./run_validate_json.sh /path/to/transcript.json"
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "❌ Error: File not found at '$INPUT_FILE'"
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔍 Validating training data at: $INPUT_FILE"
PYTHONPATH="$PROJECT_ROOT/src" python3 -c "from training.utils.common import validate_and_finalize_json; validate_and_finalize_json('$INPUT_FILE')"
echo "✅ Validation complete."
