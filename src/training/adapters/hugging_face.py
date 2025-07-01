# src/training/adapters/hugging_face.py
import json
from typing import List
from training.utils.common import TrainingItem

def save_hf_training_data(
    training_data: List[TrainingItem],
    output_path: str
):
    hf_data = []
    for item in training_data:
        completion = f"Extract: {', '.join(item.flags)}\nSummary: {item.semantic_summary}"
        hf_data.append({
            "prompt": item.prompt,
            "completion": completion
        })

    with open(output_path, 'w') as f:
        for entry in hf_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
