import json
import os
import argparse
from typing import List, Tuple
from rachel.utils.prompts import generate_shallow_prompt, PromptContext

def generate_new_prompt(context: List[str], transcript: str) -> str:
    sc = PromptContext(context=context, text=transcript)
    return generate_shallow_prompt(sc)

def validate_item(flags, summary) -> Tuple[bool, str]:
    if bool(flags) != bool(summary):
        return False, "Mismatch: flags and summary must both be present or both empty."

    if not isinstance(flags, list):
        return False, "Flags must be a list."

    for f in flags:
        if not isinstance(f, str):
            return False, f"Invalid flag type: {repr(f)}"

    if summary and not isinstance(summary, str):
        return False, f"Invalid semantic_summary type: {repr(summary)}"

    return True, ""

def update_jsonl_from_training_json(training_json_path: str, output_jsonl_path: str) -> Tuple[int, int, int, int]:
    updated_lines = []
    count_empty = 0
    count_non_empty = 0
    count_invalid = 0

    with open(training_json_path, 'r') as infile:
        data = json.load(infile)

        if isinstance(data, dict):
            data = data.get("training_data", [])

        print(f"[DEBUG] Loaded {len(data)} items from {training_json_path}")

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            context = item.get("context_used", [])
            transcript = item.get("current_text", "")
            flags = item.get("flags", [])
            semantic_summary = item.get("semantic_summary", "")

            is_valid, reason = validate_item(flags, semantic_summary)
            if not is_valid:
                print(f"[WARN] Skipping invalid item #{idx} in {training_json_path}: {reason}")
                count_invalid += 1
                continue

            if not flags and not semantic_summary:
                count_empty += 1
            else:
                count_non_empty += 1

            prompt = generate_new_prompt(context, transcript)
            completion = f"Flags: {json.dumps(flags)}\nSemanticSummary: {json.dumps(semantic_summary)}"

            updated_lines.append(json.dumps({
                "prompt": prompt,
                "completion": completion
            }))

    if updated_lines:
        with open(output_jsonl_path, 'w') as outfile:
            outfile.write('\n'.join(updated_lines))

    print(f"[REPORT] Processed file: {training_json_path}")
    print(f"         ➤ Total items loaded  : {len(data)}")
    print(f"         ➤ Written to output   : {len(updated_lines)}")
    print(f"             ├─ Empty examples : {count_empty}")
    print(f"             └─ With flags     : {count_non_empty}")
    print(f"         ➤ Invalid items skipped: {count_invalid}")

    return len(data), len(updated_lines), count_empty, count_non_empty

def process_files(input_dir: str, output_dir: str, in_place: bool = False):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    print(f"[INFO] Input directory: {input_dir}")
    if not in_place:
        print(f"[INFO] Output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    found_any = False
    total_files = 0
    grand_total_loaded = 0
    grand_total_written = 0
    grand_total_empty = 0
    grand_total_flagged = 0

    for root, _, files in os.walk(input_dir):
        if "training.json" not in files:
            continue

        found_any = True
        input_path = os.path.join(root, "training.json")
        rel_path = os.path.relpath(root, input_dir)
        output_path = os.path.join(output_dir, rel_path, "training_hf.jsonl")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"[INFO] Processing {input_path}...")
        loaded, written, empty, flagged = update_jsonl_from_training_json(input_path, output_path)

        total_files += 1
        grand_total_loaded += loaded
        grand_total_written += written
        grand_total_empty += empty
        grand_total_flagged += flagged

    if not found_any:
        print("[WARN] No training.json files found (even in subdirectories).")
    else:
        print(f"\n[SUMMARY] ✅ Finished processing {total_files} files")
        print(f"         ➤ Total items loaded : {grand_total_loaded}")
        print(f"         ➤ Total written out  : {grand_total_written}")
        print(f"             ├─ Empty examples: {grand_total_empty}")
        print(f"             └─ With flags    : {grand_total_flagged}")
        print(f"         ➤ Skipped or invalid : {grand_total_loaded - grand_total_written}")

def main():
    parser = argparse.ArgumentParser(description="Generate updated training_hf.jsonl files from training.json source files.")
    parser.add_argument("--input-dir", required=True, help="Directory containing training.json files.")
    parser.add_argument("--output-dir", help="Directory to save training_hf.jsonl files.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite training_hf.jsonl files in-place.")

    args = parser.parse_args()

    if args.in_place:
        process_files(args.input_dir, args.input_dir, in_place=True)
    else:
        if not args.output_dir:
            parser.error("Either --output-dir or --in-place must be specified.")
        process_files(args.input_dir, args.output_dir, in_place=False)

if __name__ == "__main__":
    main()
