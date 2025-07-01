import os
import json
from pathlib import Path

# Set the root directory for training data
DATA_ROOT = "/DATA"

def analyze_training_data(base_dir: str):
    total = 0
    positives = 0
    negatives = 0
    bad_segments = []

    base_path = Path(base_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"❌ Base path not found: {base_dir}")

    for folder in base_path.iterdir():
        if not folder.is_dir():
            continue

        train_path = folder / "training.json"
        if not train_path.exists():
            print(f"⚠️ No training.json in: {folder.name}")
            continue

        try:
            with open(train_path, "r") as f:
                segments = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {train_path}: {e}")
            continue

        for segment in segments:
            total += 1
            flags = segment.get("output", [])
            summary = segment.get("semantic_summary", "").strip()

            if flags:
                positives += 1
            else:
                if summary:
                    bad_segments.append({
                        "file": str(train_path),
                        "text": segment.get("text", "")[:60],
                        "summary": summary
                    })
                negatives += 1

    print(f"\n📊 Summary:")
    print(f"  Total segments: {total}")
    print(f"  Positive samples (with flags): {positives}")
    print(f"  Negative samples (no flags): {negatives}")
    print(f"  ❌ Bad segments (no flags but has summary): {len(bad_segments)}")

    if bad_segments:
        print("\n⚠️ Bad Segment Samples:")
        for b in bad_segments[:5]:
            print(f"- {b['file']} → {b['text']} … (summary: {b['summary']})")

if __name__ == "__main__":
    analyze_training_data(DATA_ROOT)
