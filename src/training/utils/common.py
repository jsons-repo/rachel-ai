# src/training/common.py

import os
import re
import json
from glob import glob
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from rachel.core.model import RawTranscriptSegment
from rachel.utils.common import merge_segments_by_words_with_cutoff


BASE_OUTPUT_ROOT = "/DATA"

@dataclass
class GptOutput:
    start: float
    end: float
    duration: float
    text: str
    prompt: str
    flags: List[str]
    filename: str
    semantic_summary: str
    context_used: List[str] 
    current_text: str

@dataclass
class TrainingItem:
    prompt: str
    flags: List[str]
    semantic_summary: str
    context_used: List[str] 
    current_text: str

def safe_base_name(filename: str) -> str:
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    name = re.sub(r'[^a-z0-9-]+', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name
    

def derive_output_path(wav_path: str) -> str:
    base_name = safe_base_name(wav_path)
    output_dir = os.path.join(BASE_OUTPUT_ROOT, base_name)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, "whisper.json")

def analyze_training_jsonl(base_path: str):
    all_files = glob(f"{base_path}/*/training_hf.jsonl")
    total = 0
    positive = 0
    negative = 0
    valid = 0
    invalid = 0

    for file_path in all_files:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, start=1):
                total += 1
                try:
                    obj = json.loads(line)
                    if 'completion' in obj:
                        flags_section = obj['completion'].split("Summary:")[0]
                        flags_line = flags_section.replace("Extract:", "").strip()
                        if flags_line:
                            positive += 1
                        else:
                            negative += 1

                    item_for_validation = {
                        "flags": obj.get("flags", []),
                        "semantic_summary": obj.get("semantic_summary", ""),
                        "current_text": obj.get("completion", "")
                    }

                    validated = validate_training_item(item_for_validation)
                    if validated is not None:
                        valid += 1
                    else:
                        invalid += 1
                        print(f"❌ Invalid item at {file_path}, line {line_num}:\n  → {item_for_validation}\n")

                except json.JSONDecodeError:
                    print(f"⚠️ Skipping malformed line in {file_path}, line {line_num}")

    print("📊 Training Data Analysis:")
    print(f"  Total examples: {total}")
    print(f"  Positive examples (with flags): {positive}")
    print(f"  Negative examples (empty flags): {negative}")
    print(f"  Valid training items: {valid}")
    print(f"  Invalid training items: {invalid}")


def fix_empty_flags_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    If there are no flags, force semantic_summary to be "".
    """
    if not item.get("flags"):
        item["semantic_summary"] = ""
    return item

def filter_invalid_flags(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Ensures each flag is an exact substring of current_text.
    If a flag isn't found, try matching a normalized version.
    If no match, remove it.
    If all flags are removed, item may become invalid.
    """
    current_text = item.get("current_text", "")
    if not isinstance(current_text, str):
        return None  # Skip malformed entries

    original_flags = item.get("flags", [])
    valid_flags = []

    text_words = re.findall(r"\b\w[\w'’-]*\b", current_text)

    for flag in original_flags:
        if not isinstance(flag, str):
            continue

        # 1. Exact match
        if flag in current_text:
            valid_flags.append(flag)
            continue

        # 2. Normalized match (case-insensitive, stripped)
        norm_flag = flag.lower().strip()
        match = next(
            (word for word in text_words if word.lower().strip() == norm_flag),
            None
        )
        if match:
            valid_flags.append(match)  # capture original casing
            continue

    item["flags"] = valid_flags

    # If all flags removed AND summary present, nuke summary too
    if not valid_flags:
        item["semantic_summary"] = ""

    return item if valid_flags or item.get("semantic_summary") == "" else None

def normalize_flags(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures 'flags' is always a list, even if null or missing.
    """
    if not isinstance(item.get("flags"), list):
        item["flags"] = []
    return item

def validate_training_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    item = normalize_flags(item)
    item = fix_empty_flags_summary(item)
    item = filter_invalid_flags(item)
    return item

def validate_and_finalize_json(json_path: str) -> None:
    """
    Loads a wrapped training JSON with a `training_data` list and applies cleanup rules.
    Saves the result back to the same file.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    if "training_data" not in data or not isinstance(data["training_data"], list):
        raise ValueError(f"Expected 'training_data' to be a list in {json_path}")

    original_len = len(data["training_data"])

    data["training_data"] = [
        validate_training_item(item) for item in data["training_data"]
    ]

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Validated {original_len} training items.")



def merge_segments_entire_file(
    segments: List[RawTranscriptSegment],
    min_duration: float = 3.5,
    max_buffer: int = 5
) -> List[RawTranscriptSegment]:
    result_segments: List[RawTranscriptSegment] = []
    last_end_time = 0.0
    buffer: List[RawTranscriptSegment] = []

    


    for seg in segments:

        buffer.append(seg)

        result = merge_segments_by_words_with_cutoff(
            buffer,
            chunk_offset=buffer[0].start,
            cutoff=min(last_end_time, buffer[0].start)
        )

        if not result:
            continue

        start, end, text = result
        duration = end - start

        if duration >= min_duration or len(buffer) >= max_buffer:
            result_segments.append(
                RawTranscriptSegment(
                    start=start,
                    end=end,
                    text=text,
                    words=None,  # Optional: use merged words here if applicable
                    raw_backend_data={"merged_from": len(buffer)}
                )
            )
            last_end_time = end
            buffer = []

    if buffer:
        result = merge_segments_by_words_with_cutoff(
            buffer,
            chunk_offset=buffer[0].start,
            cutoff=min(last_end_time, buffer[0].start)
        )
        if result:
            start, end, text = result
            duration = end - start
            result_segments.append(
                RawTranscriptSegment(
                    start=start,
                    end=end,
                    text=text,
                    words=None,
                    raw_backend_data={"merged_from": len(buffer)}
                )
            )

    return result_segments
