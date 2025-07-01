#!/bin/bash
set -e

echo "🔍 Analyzing training data..."
PYTHONPATH=../../src python3 -m training.utils.analyze_training_data
