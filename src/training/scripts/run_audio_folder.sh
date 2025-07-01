#!/bin/bash
set -e

AUDIO_DIR="/DATA/AUDIO"
DATA_ROOT="/DATA"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

normalize_name() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | \
    sed -E 's/[^a-z0-9]+/-/g' | \
    sed -E 's/^-+|-+$//g'
}

shopt -s nullglob
IFS=$'\n'

readarray -t AUDIO_FILES < <(find "$AUDIO_DIR" -type f \( -iname '*.wav' -o -iname '*.mp3' -o -iname '*.mp4' \))

for AUDIO_FILE in "${AUDIO_FILES[@]}"; do
  if [[ ! -f "$AUDIO_FILE" ]]; then
    continue
  fi

  BASE_NAME=$(basename "$AUDIO_FILE")
  BASE_NAME="${BASE_NAME%.*}"
  SAFE_NAME=$(normalize_name "$BASE_NAME")

  OUTPUT_DIR="${DATA_ROOT}/${SAFE_NAME}"
  WHISPER_JSON="${OUTPUT_DIR}/whisper.json"
  GPT_OUTPUT_JSON="${OUTPUT_DIR}/gpt_output.json"
  TRAINING_JSON="${OUTPUT_DIR}/training.json"
  TRAINING_HF_JSON="${OUTPUT_DIR}/training_hf.jsonl"

  echo "🎙️ Processing: $AUDIO_FILE"
  echo "📁 Output directory: $OUTPUT_DIR"

  echo "📥 Transcribing with Whisper..."
  PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.wave_to_whisper "$AUDIO_FILE"

  echo "💬 Converting Whisper to GPT output..."
  PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.whisper_to_gpt "$WHISPER_JSON"

  echo "📦 Building training.json..."
  PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.gpt_to_training "$GPT_OUTPUT_JSON"

  echo "🧹 Validating training.json..."
  PYTHONPATH="$PROJECT_ROOT/src" python3 -c "from training.utils.common import validate_and_finalize_json; validate_and_finalize_json('$TRAINING_JSON')"

  if [[ ! -f "$TRAINING_JSON" ]]; then
    echo "❌ training.json not created!"
  fi

  if [[ ! -f "$TRAINING_HF_JSON" ]]; then
    echo "❌ training_hf.jsonl not created!"
  fi
  
  echo "✅ All done for: $AUDIO_FILE"
  echo "📄 Outputs:"
  echo " - Whisper:   $WHISPER_JSON"
  echo " - GPT:       $GPT_OUTPUT_JSON"
  echo " - Training:  $TRAINING_JSON"
  echo " - HF Format: $TRAINING_HF_JSON"

done

echo "🏁 Pipeline complete for all files."
