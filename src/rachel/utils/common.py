# src/rachel/utils/common.py
import ast
import json
import pprint
import re
from dataclasses import asdict, is_dataclass
from typing import Any, List, Optional, Tuple
from rachel.core.model import Flag, FlagSource, ExitReason, RawTranscriptSegment

DEBUG_VERBOSE = True


def normalize(text: str) -> str:
    return text.strip().lower().replace("’", "'").rstrip(".?!\n")

def extract_json_block(raw_output: str) -> dict:
    """
    Robustly extract JSON from LLM output that may be wrapped in markdown-style fences.
    """
    stripped = raw_output.strip()

    # Look for the first '{' and assume that's the real JSON start
    json_start = stripped.find('{')
    if json_start == -1:
        raise ValueError("No JSON object found")

    json_str = stripped[json_start:]

    # Remove trailing ``` if present
    if json_str.endswith("```"):
        json_str = json_str[:-3].strip()

    return json.loads(json_str)


def parse_deep_response(raw_response: str, prompt: str, segment_id: str) -> Optional[Flag]:
    try:
        parsed = extract_json_block(raw_response)
    except (json.JSONDecodeError, ValueError) as e:
        print("❌ JSON parse error:", e)
        return None

    if isinstance(parsed, dict):
        items = [parsed]
    elif isinstance(parsed, list):
        items = parsed
    else:
        print("❌ Unexpected response format:", type(parsed))
        return None

    by_claim = {
        normalize(item["claim"]): item
        for item in items
        if isinstance(item, dict) and "claim" in item
    }

    if not by_claim:
        print("⚠️ No valid claim returned from deep LLM — skipping.")
        return None

    _, entry = next(iter(by_claim.items()))
    claim_raw = entry.get("claim", "")
    if not isinstance(claim_raw, str):
        print(f"❌ Invalid claim format: expected string, got {type(claim_raw)} — value: {claim_raw}")
        return None

    try:
        exit_reason = ExitReason(entry.get("exit_reason", "NONE").upper())
    except Exception:
        exit_reason = ExitReason.NONE

    try:
        severity = float(entry.get("severity", 0.0))
    except Exception:
        severity = 0.0

    return Flag(
        id=f"{segment_id}_deep",
        matches=[s.strip() for s in claim_raw.split("|")],
        summary=entry.get("headline", ""),
        text=entry.get("analysis", ""),
        severity=severity,
        source=FlagSource.DEEP,
        category=None,
        semantic_summary=entry.get("semantic_summary", ""),
        source_prompt=prompt,
        exit_reason=exit_reason
    )


def strip_markdown_backticks(s: str) -> str:
    """
    Remove surrounding markdown code fences like ```json ... ```
    """
    return re.sub(r"^```(?:json)?\n?|```$", "", s.strip(), flags=re.IGNORECASE)


def extract_first_json_brace_block(s: str) -> str:
    """
    Extracts the first {...} block using a balanced brace scan.
    Useful for grabbing the first valid JSON blob in messy GPT output.
    """
    stack = []
    start = None
    for i, c in enumerate(s):
        if c == '{':
            if not stack:
                start = i
            stack.append(c)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    return s[start:i+1]
    return s  # fallback to full string if no balanced braces found


def attempt_json_parse(s: str) -> Any:
    """
    Safely attempt to parse a JSON string.
    Returns a dict, list, str, etc., or None on failure.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def parse_double_encoded_json(s: str) -> dict | None:
    """
    Handles case where JSON is embedded as a string within JSON.
    E.g., GPT returns something like: "{\"headline\": \"...\", ...}"
    """
    first = attempt_json_parse(s)
    if isinstance(first, str):
        return attempt_json_parse(first)
    if isinstance(first, dict):
        return first
    return None


def desperate_single_to_double_quote_fix(s: str) -> dict | None:
    """
    Final attempt: replace single quotes with double quotes and try parsing.
    Risky but occasionally helps with GPT formatting bugs.
    """
    try:
        return json.loads(s.replace("'", '"'))
    except Exception:
        return None


def parse_gpt_json_response(raw: str) -> dict:
    """
    Attempts to safely extract and parse a GPT-style JSON response, even if:
    - It's double-encoded
    - Wrapped in markdown
    - Includes text before/after the JSON
    - Has minor syntax errors

    Returns a parsed dict or raises ValueError on failure.
    """
    cleaned = strip_markdown_backticks(raw)

    # Try direct parse
    if parsed := attempt_json_parse(cleaned):
        if isinstance(parsed, dict):
            return parsed

    # Try double-encoded JSON
    if parsed := parse_double_encoded_json(cleaned):
        return parsed

    # Try extracting JSON blob via balanced braces
    brace_block = extract_first_json_brace_block(cleaned)
    if parsed := attempt_json_parse(brace_block):
        if isinstance(parsed, dict):
            return parsed

    # Try final hail-mary fix: single to double quotes
    if parsed := desperate_single_to_double_quote_fix(cleaned):
        return parsed

    raise ValueError("❌ Failed to parse GPT response as JSON:\n" + raw)



def parse_extract_list(raw: str) -> List[str]:
    patterns = [
        r"(?i)flags\s*[:：]\s*(\[[^\]]*\])",  # Flags: ["..."]
    ]

    for pattern in patterns:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            list_text = match.group(1)
            try:
                return json.loads(list_text)
            except json.JSONDecodeError:
                # fallback: try naive split
                return [
                    f.strip().strip('"').strip("'")
                    for f in list_text.strip("[]").split(",")
                    if f.strip()
                ]

    return []



def parse_summary_text(raw: str) -> str:
    patterns = [
        r"(?i)semanticsummary\s*[:：]\s*['\"](.+?)['\"]",  # SemanticSummary: "..."
        r"(?i)summary\s*[:：]\s*(.+)",  # Fallback: Summary:
    ]

    for pattern in patterns:
        match = re.search(pattern, raw, re.DOTALL)
        if match:
            return match.group(1).strip()

    # Fallback: last sentence
    fallback_sentences = re.split(r"[.?!]\s+", raw.strip())
    if fallback_sentences:
        return fallback_sentences[-1].strip()

    return ""



def parse_shallow_output(raw: str) -> Tuple[List[str], str]:
    """
    Parses shallow LLM output with 'Extract:' and 'Summary:' sections.

    Returns:
      - A list of strings from the 'Extract' section (comma-delimited, quotes optional).
      - A summary string from the 'Summary' section (or fallback last sentence).
    """
    extract = parse_extract_list(raw)
    summary = parse_summary_text(raw)
    return extract, summary


def debug(*objs):
    """
    Print debug info cleanly, suppressing messy escape sequences inside strings.
    """

    if DEBUG_VERBOSE == False:
        pass

    def clean(obj):
        if is_dataclass(obj):
            obj = asdict(obj)

        # Try to parse JSON strings inside values to make them readable
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean(i) for i in obj]
        elif isinstance(obj, str):
            # Try parsing as JSON if it's likely JSON
            stripped = obj.strip()
            if (stripped.startswith("{") and stripped.endswith("}")) or \
               (stripped.startswith("[") and stripped.endswith("]")):
                try:
                    return clean(json.loads(obj))
                except Exception:
                    pass
            # Collapse multiline strings
            return obj.replace("\n", " ").replace("  ", " ").strip()
        return obj

    for obj in objs:
        cleaned = clean(obj)
        if DEBUG_VERBOSE:
            pprint.pprint(cleaned, width=120, compact=True)
        else:
            print(cleaned)

def merge_segments_by_words_with_cutoff(
    segments: List[RawTranscriptSegment],
    chunk_offset: float,
    cutoff: float = 0.0,
    verbose: bool = False,
) -> Optional[tuple[float, float, str]]:
    merged_words = []

    for seg_idx, seg in enumerate(segments):
        if seg.words:
            for word in seg.words:
                raw_start = word.start
                raw_end = word.end
                word_start = chunk_offset + raw_start
                word_end = chunk_offset + raw_end

                if word_end <= cutoff:
                    continue

                merged_words.append((word_start, word_end, word.text.strip()))
        else:
            if verbose:
                debug("No words in segment!")

    if not merged_words:
        debug("No words made it past the cutoff.")
        return None

    start = merged_words[0][0]
    end = merged_words[-1][1]
    text = " ".join(w for _, _, w in merged_words)

    if verbose:
        debug(f"\n✅ Merged segment: {start:.2f}–{end:.2f} ({end - start:.2f}s)")

    return start, end, text




