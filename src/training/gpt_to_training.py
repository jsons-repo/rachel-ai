# src/training/gpt_to_training.py

import os
import argparse
import json
from typing import List

from rachel.core.config import get_config
from rachel.utils.prompts import generate_shallow_prompt, PromptContext
from training.adapters.hugging_face import save_hf_training_data
from training.utils.common import(
    GptOutput, 
    TrainingItem, 
    BASE_OUTPUT_ROOT,
)

def load_gpt_outputs(path: str) -> List[GptOutput]:
    with open(path, 'r') as f:
        data = json.load(f)
    return [GptOutput(**item) for item in data]


def convert_to_training_data(gpt_outputs: List[GptOutput]) -> List[TrainingItem]:
    training_data = []
    for entry in gpt_outputs:
        sc = PromptContext(
            context=[s.strip() for s in entry.context_used],
            text=entry.current_text.strip()
        )
        prompt = generate_shallow_prompt(sc)
        training_data.append(
            TrainingItem(
                prompt=prompt, 
                flags=entry.flags,
                semantic_summary=entry.semantic_summary,
                current_text=entry.current_text,
                context_used=entry.context_used
            )
        )
    return training_data


def save_training_data(
    training_data: List[TrainingItem],
    output_path: str,
    filename: str,
    duration: float
):
    cfg = get_config()
    tcfg = cfg.model.transcription

    payload = {
        "filename": filename,
        "total_segments": len(training_data),
        "duration": round(duration, 2),
        "whisper": {
            "CHUNK_DURATION": cfg.audio.chunk_duration,
            "OVERLAP_DURATION": cfg.audio.overlap_duration,
            "BEAM_SIZE": tcfg.beam_size,
            "TRANSCRIBE_NAME": tcfg.repo,
            "FORMAT": cfg.audio.format if hasattr(cfg.audio, 'format') else "N/A",
            "TRANSCRIBE_WORD_TIMESTAMPS": tcfg.word_timestamps,
        },
        "generated_by": cfg.model.deep_LLM.name,
        "training_data": [
            {
                "prompt": item.prompt,
                "flags": item.flags,
                "semantic_summary": item.semantic_summary,
                "context_used": item.context_used,
                "current_text": item.current_text,
            } for item in training_data
        ]
    }
    with open(output_path, 'w') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Convert GPT outputs into training prompt/response pairs.")
    parser.add_argument("path_to_gpt_output", help="Path to gpt_output.json")
    args = parser.parse_args()

    gpt_outputs = load_gpt_outputs(args.path_to_gpt_output)

    if not gpt_outputs:
        print("❌ No GPT outputs found.")
        return

    print(f"🔁 Converting {len(gpt_outputs)} outputs to training format...")
    training_data = convert_to_training_data(gpt_outputs)

    total_duration = sum(entry.duration for entry in gpt_outputs)

    base_name = os.path.basename(os.path.dirname(args.path_to_gpt_output))
    output_path = os.path.join(BASE_OUTPUT_ROOT, base_name, "training.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"💾 Saving training data to {output_path}...")
    save_training_data(training_data, output_path, filename=gpt_outputs[0].filename, duration=total_duration)

    hf_output_path = os.path.join(BASE_OUTPUT_ROOT, base_name, "training_hf.jsonl")
    print(f"💾 Saving HF-compatible training data to {hf_output_path}...")
    save_hf_training_data(training_data, hf_output_path)

    print("✅ Done.")


if __name__ == "__main__":
    main()
