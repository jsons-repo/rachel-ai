#!/bin/bash

set -e

echo "🔍 Running training data validation for training_hf.jsonl files..."

# Set the data root directory
DATA_ROOT="/DATA"

# Set PYTHONPATH to root of the project (2 levels up from this script)
PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/src" \
python3 -c "from training.utils.common import analyze_training_jsonl; analyze_training_jsonl('${DATA_ROOT}')"

echo "✅ Done checking training data."

