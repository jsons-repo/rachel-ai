# src/training/whisper_to_gpt.py

import os
import argparse
import json
from openai import OpenAI
from typing import List, Deque, Any
from collections import deque
from dataclasses import asdict

from rachel.core.config import get_config
from rachel.core.model import RawTranscriptWord, RawTranscriptSegment
from training.utils.common import (
    GptOutput,
    BASE_OUTPUT_ROOT,
    merge_segments_entire_file
)

# Establish client
client = OpenAI(api_key=get_config().deep_api_key)

# Rolling context shared across batches, simulating a conversation memory
context: Deque[RawTranscriptSegment] = deque(maxlen=get_config().summarization.shallow_context_window)


def get_prompt_context(_context: Deque[RawTranscriptSegment]) -> List[str]:
    return [seg.text.strip() for seg in _context]


def get_prompt_current(segment: RawTranscriptSegment) -> str:
    return segment.text.strip()

def build_batched_prompt(items: List[dict]) -> str:
    return f"""You are generating training data for a model that extracts interesting items from podcasts worth investigating, fact-checking, or learning about.

The model serves THREE roles:
1. **Fact-checker**: Flag controversial or questionable claims
2. **Educator**: Flag fascinating tech/concepts people should know about (like CRISPR's dual-use potential)
3. **Conversation enhancer**: Flag specific, remarkable things that add depth

You'll receive items with this structure:
{{
  "id": int,
  "context": [str],  # Use only for context, do not extract from context
  "transcript": str  # Extract from here only
}}

For each item, extract:
- **flags**: Interesting verbatim substrings from the transcript
- **semantic_summary**: One factual sentence describing the claim/concept

## What to Flag:

### ALWAYS Flag:
- Specific claims with numbers, measurements, or statistics
- Specific technologies with profound implications (e.g., CRISPR, AGI, brain-computer interfaces)
- ANY year/date in a political, scientific, or military context
- Named studies, experiments, operations, or programs
- Specific tools/sites/apps that do something unusual or remarkable
- Historical events, especially obscure or revisionist ones
- Scientific phenomena that challenge intuition or common understanding
- Weapons, military systems, or dual-use technologies
- Named technical or theoretical concepts, especially in:
  - **Physics** (e.g., Planck's constant, Lagrange points, Lorentz contraction)
  - **Math/Computation** (e.g., cellular automata, NP-complete problems, Gödel's incompleteness theorem)
  - **Biology/Chemistry** (e.g., cytokine storms, RNA splicing, carbon nanotubes)
- Mentions of **chemical elements or isotopes**, especially with notable properties (e.g., "helium-3 is rare on Earth")
- **Quotes** from or references to notable scientists, philosophers, or historical figures (e.g., "Einstein said 'God does not play dice'")

### The "Dinner Party Test":
Would this make people at dinner go "Wait, tell me more about that"?
- ❌ "YouTube has videos" (everyone knows)
- ✅ "NUKEMAP lets you simulate nuclear detonations" (specific, remarkable)
- ❌ "Scientists study things" (generic)
- ✅ "Scientists can create mirror life" (specific, mind-blowing)

If you're unsure — ask: Could I Google this phrase and get a cool rabbit hole of links?
If yes → include it. If no → skip it.

### DON'T Flag:
- Common platforms without specific context (e.g., "social media", "YouTube")
- Generic or vague phrases (e.g., "technology", "overcrowded streets", "science fiction")
- Well-known facts with no new angle
- Standalone first names

### Filtering Rules:
- ❌ Skip anything that’s generic, obvious, or widely known
- ✅ Only include phrases that are **specific, investigable, or surprising**
- ❌ If nothing meets the bar, return an empty `flags` array and empty `semantic_summary`

## Critical:
- Return EXACTLY one object per input item
- Each object has ONE `semantic_summary` covering ALL `flags` in that transcript
- Empty transcripts get empty `flags` array and empty string semantic_summary
- Maintain input order - all `id`s must be preserved

## Output Format:
For EACH input item, return ONE object with:
- `id`: The item's id
- `flags`: Array of verbatim substrings (0–3 items)
- `semantic_summary`: Single sentence summarizing the claim/concept

Return a JSON array of objects (one per input item):
[
  {{
    "id": 1,
    "flags": ["CRISPR", "weaponized viruses", "bioweapons"],
    "semantic_summary": "CRISPR technology could be used to create weaponized viruses"
  }},
  {{
    "id": 2,
    "flags": [],
    "semantic_summary": ""
  }},
  {{
    "id": 3,
    "flags": ["Operation Northwoods", "false flag", "1962"],
    "semantic_summary": "Operation Northwoods was a proposed false flag operation in 1962"
  }}
]

## Examples:

Input item:
{{
  "id": 1,
  "context": ["They were talking about breakthroughs in genetics and what might be possible if the wrong hands got ahold of it."],
  "transcript": "CRISPR could make bioweapons"
}}
Output:
{{
  "id": 1,
  "flags": ["CRISPR", "bioweapons"],
  "semantic_summary": "CRISPR technology could be used to create bioweapons"
}}

Input item:
{{
  "id": 2,
  "context": ["They were listing covert operations from the Cold War that later became declassified."],
  "transcript": "In 1953 the CIA started MK-Ultra"
}}
Output:
{{
  "id": 2,
  "flags": ["1953", "CIA", "MK-Ultra"],
  "semantic_summary": "CIA began MK-Ultra mind control experiments in 1953"
}}

Input item:
{{
  "id": 3,
  "context": ["The speaker was offering general thoughts on how pop culture influences urban planning."],
  "transcript": "Technology and science fiction often inspire visions of future cities."
}}
Output:
{{
  "id": 3,
  "flags": [],
  "semantic_summary": ""
}}

Input item:
{{
  "id": 42,
  "context": ["We were at CERN last fall when the new detector array came online."],
  "transcript": "The Higgs boson was confirmed at around 125.35 GeV, which matched theoretical predictions. What’s wild is how that discovery relied on symmetry breaking and the role of the Brout–Englert–Higgs mechanism."
}}
Output:
{{
  "id": 42,
  "flags": ["Higgs boson", "125.35 GeV", "Brout–Englert–Higgs mechanism"],
  "semantic_summary": "The Higgs boson was confirmed at 125.35 GeV through the Brout–Englert–Higgs mechanism involving symmetry breaking."
}}

Input item:
{{
  "id": 51,
  "context": ["There’s been a lot of talk about how the media landscape has changed, especially after the pandemic."],
  "transcript": "Streaming platforms are basically the new cable, and honestly, social media influences everything now — even the news."
}}
Output:
{{
  "id": 51,
  "flags": [],
  "semantic_summary": ""
}}





Return ONLY a JSON array:
[
  {{
    "id": 1,
    "flags": ["CRISPR", "weaponized viruses"],
    "semantic_summary": "CRISPR technology could be used to create weaponized viruses"
  }}
]

Input:
{json.dumps(items, ensure_ascii=False, indent=2)}
""".strip()


def query_gpt4(prompt: str) -> List[dict]:
    cfg = get_config()
    model_name = cfg.model.deep_LLM.name

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    if not content:
        raise ValueError("GPT-4 returned empty response.")

    if content.lower().startswith("output:"):
        content = content.partition("Output:")[2].strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").removesuffix("```").strip()
    elif content.startswith("```"):
        content = content.removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(content)
        if not isinstance(parsed, list):
            raise ValueError("Expected a list of JSON objects.")
        for item in parsed:
            if not isinstance(item, dict) or "id" not in item or "flags" not in item or "semantic_summary" not in item:
                raise ValueError(f"Invalid format in item: {item}")
        return parsed
    except json.JSONDecodeError as e:
        print("❌ GPT-4 response was not valid JSON:")
        print(content)
        raise e


def load_segments(path: str) -> List[RawTranscriptSegment]:
    with open(path, 'r') as f:
        data = json.load(f)

    segments = []
    for idx, item in enumerate(data):
        words_raw = item.get("words")
        if isinstance(words_raw, list):
            try:
                item["words"] = [
                    RawTranscriptWord(
                        start=w["start"],
                        end=w["end"],
                        text=w["text"],
                        confidence=w.get("confidence")
                    ) for w in words_raw
                ]
            except Exception as e:
                print(f"⚠️ Error parsing words: {e}")
                item["words"] = None
        else:
            print("⚠️ No valid 'words' list found")
            item["words"] = None

        try:
            segments.append(RawTranscriptSegment(**item))
        except Exception as e:
            print(f"❌ Failed to create RawTranscriptSegment: {e}")
            continue

    return segments




def save_gpt_outputs(outputs: List[GptOutput], filename: str):
    with open(filename, 'w') as f:
        json.dump([asdict(o) for o in outputs], f, ensure_ascii=False, indent=2)


def create_batches(items: List[Any], batch_size: int) -> List[List[Any]]:
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def process_segments(segments: List[RawTranscriptSegment], output_path: str) -> List[GptOutput]:
    cfg = get_config()
    batch_size = cfg.training.gpt_batch_size

    outputs: List[GptOutput] = []
    all_batches = create_batches(segments, batch_size)

    seen_keys = set()
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            for item in json.load(f):
                outputs.append(GptOutput(**item))
                seen_keys.add((round(item["start"], 2), round(item["end"], 2)))

    for batch_index, batch in enumerate(all_batches):
        batch_key = [(round(s.start, 2), round(s.end, 2)) for s in batch]
        if all(key in seen_keys for key in batch_key):
            print(f"⏩ Skipping batch {batch_index+1}: already processed.")
            continue

        print(f"⚙️ Processing batch {batch_index + 1}/{len(all_batches)} ({len(batch)} segments)...")

        input_items = []
        metadata_by_id = {}

        for i, segment in enumerate(batch):
            seg_id = i
            context_text = get_prompt_context(context)
            current_text = get_prompt_current(segment)
            input_items.append({
                "id": seg_id,
                "context": context_text,
                "transcript": current_text
            })
            metadata_by_id[seg_id] = {
                "segment": segment,
                "context_text": context_text,
                "current_text": current_text
            }
            context.append(segment)

        prompt = build_batched_prompt(input_items)

        try:
            results = query_gpt4(prompt)
        except Exception as e:
            print(f"[ERROR] GPT-4 query failed on batch {batch_index}: {e}")
            results = [{"id": item["id"], "flags": [], "semantic_summary": "General conversation without specific claims"} for item in input_items]

        for result in results:
            meta = metadata_by_id[result["id"]]
            seg = meta["segment"]
            gpt_output = GptOutput(
                start=round(seg.start, 2),
                end=round(seg.end, 2),
                duration=round(seg.end - seg.start, 2),
                text=seg.text,
                prompt=prompt,
                flags=result.get("flags", []),
                semantic_summary=result.get("semantic_summary", ""),
                context_used=meta["context_text"],
                current_text=meta["current_text"],
                filename=output_path
            )
            outputs.append(gpt_output)
            seen_keys.add((gpt_output.start, gpt_output.end))

        with open(output_path, "w") as f:
            json.dump([asdict(o) for o in outputs], f, ensure_ascii=False, indent=2)

    return outputs


def main():
    parser = argparse.ArgumentParser(description="Create training data from WhisperSegments")
    parser.add_argument("path_to_file", help="Path to input JSON file of WhisperSegments")
    args = parser.parse_args()

    if not os.path.exists(args.path_to_file):
        raise FileNotFoundError(f"Input file not found: {args.path_to_file}")

    print(f"Loading segments from: {args.path_to_file}")
    raw_segments = load_segments(args.path_to_file)

    if not raw_segments:
        raise ValueError("Input file contains no valid WhisperSegments.")
    print(f"Loaded {len(raw_segments)} raw segments.")

    print(f"🔁 Merging raw segments...")
    merged_segments = merge_segments_entire_file(raw_segments)

    if len(merged_segments) < 2:
        merged_segments = raw_segments[:]

    print("Sample after merging:")
    for s in merged_segments[:3]:
        print(f"  → [{s.start:.2f}-{s.end:.2f}] {s.text[:60]}...")

    # Fix: get the folder name containing the whisper.json file
    base_name = os.path.basename(os.path.dirname(args.path_to_file))
    output_dir = os.path.join(BASE_OUTPUT_ROOT, base_name)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "gpt_output.json")
    if os.path.exists(output_path):
        i = 1
        while True:
            versioned_path = os.path.join(output_dir, f"gpt_output_{i:02d}.json")
            if not os.path.exists(versioned_path):
                print(f"🔁 Renaming existing gpt_output.json → gpt_output_{i:02d}.json")
                os.rename(output_path, versioned_path)
                break
            i += 1


    print(f"Processing {len(merged_segments)} segments with {get_config().model.deep_LLM.name}...")
    gpt_outputs = process_segments(merged_segments, output_path=output_path)

    print(f"💾 Saving outputs to {output_path}")
    save_gpt_outputs(gpt_outputs, output_path)
    print(f"✅ Done.")


if __name__ == "__main__":
    main()
