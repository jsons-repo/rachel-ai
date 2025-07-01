#!/bin/bash

set -e

TRAIN_IN="DATA/"

if [ -z "$1" ]; then
  echo "❌ Usage: ./run_whisper.sh filename.wav"
  exit 1
fi

if [[ "$1" = /* ]]; then
  WAV_PATH="$1"  # Absolute path
else
  WAV_PATH="$TRAIN_IN/$1"
fi

if [ ! -f "$WAV_PATH" ]; then
  echo "❌ File not found: $WAV_PATH"
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "📂 Running whisper on: $WAV_PATH"
PYTHONPATH="$PROJECT_ROOT/src" python3 -m training.wave_to_whisper "$WAV_PATH"
