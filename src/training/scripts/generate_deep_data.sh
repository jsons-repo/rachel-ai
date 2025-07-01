#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "❌ Usage: ./scripts/generate_deep_data.sh [foldername]"
  exit 1
fi

FOLDER="$1"
ROOT_DIR="DATA/"
TARGET_DIR="${ROOT_DIR}/${FOLDER}"

WHISPER_JSON="${TARGET_DIR}/whisper.json"
GPT_JSON="${TARGET_DIR}/gpt_output.json"
TRAINING_JSON="${TARGET_DIR}/training.json"

# You're running from ~/projects/rachel/src/training
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT"

if [ ! -f "$WHISPER_JSON" ]; then
  echo "❌ whisper.json not found in: $TARGET_DIR"
  exit 1
fi

version_if_exists() {
  FILE="$1"
  if [ -f "$FILE" ]; then
    i=1
    while [ -f "${FILE%.*}_$(printf "%02d" $i).${FILE##*.}" ]; do
      ((i++))
    done
    mv "$FILE" "${FILE%.*}_$(printf "%02d" $i).${FILE##*.}"
    echo "🔁 Existing file renamed to: ${FILE%.*}_$(printf "%02d" $i).${FILE##*.}"
  fi
}

echo "💬 Generating GPT output from whisper.json..."
version_if_exists "$GPT_JSON"
python3 -m training.whisper_to_gpt "$WHISPER_JSON"

echo "📦 Converting to training.json..."
version_if_exists "$TRAINING_JSON"
python3 -m training.gpt_to_training "$GPT_JSON"

echo "✅ All done!"
