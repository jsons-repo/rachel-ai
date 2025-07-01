# src/rachel/utils/prompts.py

import json
from typing import Deque, Optional, List
from dataclasses import dataclass
from rachel.core.model import ShallowTranscriptContext, FlagSource, Flag
from rachel.runtime.runtime import transcript_archive, transcript_archive_lock

@dataclass
class PromptContext:
    context: List[str]
    text: str

def shallow_to_prompt_context(sc: ShallowTranscriptContext) -> PromptContext:
    return PromptContext(
        context=[seg.text.strip() for seg in sc.context],
        text=sc.current.text.strip()
    )

def generate_user_search_prompt(
    segment_id: str,
    selected_text: str,
    query: str, 
    window: int = 5
) -> Optional[str]:
    with transcript_archive_lock:
        segment = transcript_archive.get(segment_id)
        if not segment:
            print(f"⚠️ Segment ID {segment_id} not found in archive.")
            return None

        all_segments = list(transcript_archive.values())
        all_segments.sort(key=lambda s: s.start)
        idx = next((i for i, s in enumerate(all_segments) if s.id == segment_id), None)
        if idx is None:
            print(f"⚠️ Segment index not found for ID {segment_id}")
            return None

        context_window = all_segments[max(0, idx - window):idx]

    context_lines = [s.text.strip() for s in context_window]
    context_text = "\n".join(context_lines)
    query_block = f'''
The host has also included a personal note — this is **not part of the transcript**, but it reflects specific ideas or questions they want you to consider and directly address in your response:
"{query}"''' if query else ""

    return f"""
You are an expert researcher assisting podcast hosts in real time.

They’ve flagged the following quote from a guest as confusing, contentious, or especially interesting:
"{selected_text}"{query_block}

Here is the recent transcript context leading up to the flagged quote:
{context_text}

TASK:
Deliver a thorough, factual deep dive. Clarify the issue and explain how it connects to broader ideas. Focus on names, dates, history, and evidence — the kind of context that helps the host speak intelligently on-air.

Your response must include:
1. Key names, dates, and locations
2. A brief historical timeline (if applicable — skip if not)
3. The nature of the core controversy or claim
4. Major sources or evidence (or lack thereof)

RULES:
- Be neutral, factual, and clear.
- Do NOT speculate or editorialize.
- Create a headline to capture the big idea
- The body should be detailed.
- You may include line breaks (`\n\n`) in the `body` field to separate paragraphs.
- Return structured JSON output — no commentary, no extra formatting.

IMPORTANT RULES:
- You must return a valid JSON object with the exact keys listed below.
- DO NOT add or remove any keys — all 6 must be present in the output.
- It is OK if some values are empty (e.g., empty lists or strings), but every field must be included.
- DO NOT include markdown formatting like ```json.
- DO NOT write anything outside the JSON object.

Output this JSON exactly:
{{
  "headline": "...",
  "body": "...",
  "key_figures": ["Name 1", "Name 2"],
  "timeline": ["YYYYMMDD: Event", "..."]
}}
""".strip()



def generate_deepsearch_prompt(
    segment_id: str,
    window: int = 5
) -> Optional[str]:
    # 1. Pull full segment from archive
    with transcript_archive_lock:
        segment = transcript_archive.get(segment_id)
        if not segment:
            print(f"⚠️ Segment ID {segment_id} not found in archive.")
            return None

        # 2. Rebuild nearby context (sorted by start time)
        all_segments = list(transcript_archive.values())
        all_segments.sort(key=lambda s: s.start)

        idx = next((i for i, s in enumerate(all_segments) if s.id == segment_id), None)
        if idx is None:
            print(f"⚠️ Segment index not found for ID {segment_id}")
            return None

        context_window = all_segments[max(0, idx - window):idx]  # N lines before

    # 3. Build context and topic
    context_lines = [s.text.strip() for s in context_window]
    context_text = "\n".join(context_lines)

    matches = [
        m
        for flag in (segment.flags or [])
        for m in (flag.matches or [])
    ]
    topic = " | ".join(matches) if matches else segment.text.strip()

    return f"""
The user has asked for a detailed analysis of the following topic:
"{topic}"

Recent conversation context:
{context_text}

TASK:
You are an expert researcher assisting podcast hosts in real time. They’ve specifically flagged this topic as confusing, contentious, or potentially misleading — and they’ve asked you to get to the bottom of it. Your job is to deliver a thorough, factual deep dive that clarifies the issue. Assume they’re looking for names, dates, history, and evidence — the kind of context that cuts through noise and helps them speak intelligently on-air.

Your response should include:
1. Key names, dates, and locations
2. A brief historical timeline (if applicable)
3. The nature of the core controversy or claim
4. Major sources or evidence (or lack thereof)

RULES:
- Be neutral, factual, and clear.
- Do NOT speculate or editorialize.
- Use short, declarative sentences.
- Return structured JSON output — no commentary, no extra formatting.

Output this JSON exactly:
{{
  "topic": "{topic}",
  "summary": "...",
  "key_figures": ["Name 1", "Name 2"],
  "timeline": ["YYYYMMDD: Event", "..."],
  "controversy": "...",
  "evidence": "...",
}}
""".strip()



def generate_deep_prompt(sc: ShallowTranscriptContext, recent_flags: Deque[Flag]) -> str:
    print("@generate_deep_prompt", sc)
    
    context_text = json.dumps([seg.text for seg in sc.context], ensure_ascii=False)
    transcript_text = json.dumps(sc.current.text, ensure_ascii=False)

    semantic_recent_summaries = json.dumps([
        flag.semantic_summary
        for flag in recent_flags
        if flag.source == FlagSource.SHALLOW and flag.semantic_summary
    ], ensure_ascii=False)

    shallow_flag = next(
        (flag for flag in (sc.current.flags or []) if flag.source == FlagSource.SHALLOW),
        None
    )
    current_flags = json.dumps(shallow_flag.matches if shallow_flag else [], ensure_ascii=False)
    composite_claim = " | ".join(shallow_flag.matches) if shallow_flag else ""

    return f"""
You are an assistant providing fast, factual analysis of a topic in a live conversation.

Context (past {len(sc.context)} lines):
{context_text}

Last utterance:
{transcript_text}

These topics have already been analyzed recently. Unless they are clearly referenced again in a new way, do not repeat analysis:
{semantic_recent_summaries}

Topic to analyze:
{current_flags}

TASK:
- Focus only on the topic’s content — do not comment on the speaker or delivery.
- You may use context to resolve vague references or pronouns.
- Write a short headline and a brief, factual analysis.
- Score the severity from 0–10 based on **factual accuracy**, not emotional or moral intensity:
  • 0–3 = accurate and neutral
  • 4–6 = vague, potentially misleading, or unclear
  • 7–10 = factually false, misleading, or highly deceptive

EXIT CONDITIONS:
If the topic cannot be meaningfully analyzed (for example, if it is unclear, redundant, or lacks substance), still return a JSON object with:
  - an empty string for "analysis" and "headline"
  - a valid "exit_reason" field

Valid exit_reason values:
- "NONE" — Proceeded with a valid analysis
- "DUPLICATE" — Topic has already been evaluated
- "CONFUSING" — Statement is unclear or hard to interpret
- "INSUBSTANTIAL" — Topic is too vague, generic, or lacks content

Output one JSON object only — no commentary, no formatting:
{{
  "claim": "{composite_claim}",
  "severity": 0-10,
  "analysis": "...",
  "headline": "...",
  "exit_reason": "NONE" | "DUPLICATE" | "CONFUSING" | "INSUBSTANTIAL"
}}

IMPORTANT:
- Do NOT change the value of "claim"
- Always return valid JSON
- Do NOT wrap your response in triple backticks (e.g. ```json)
""".strip()

def generate_shallow_prompt(pc: PromptContext) -> str:
    context_block = json.dumps([p.strip() for p in pc.context])
    transcript_text = json.dumps(pc.text.strip())

    return f"""
Use the Context only to clarify meaning — extract *only* verbatim substrings from the Transcript.

Context:
{context_block}

Transcript:
{transcript_text}

TASK:
1. Extract exact phrases (verbatim substrings) from the Transcript that are interesting or worth looking up. These include:
   - Named people, countries, cities, or regions
   - Dates or standalone years
   - Institutions, companies, or government agencies
   - Government programs, units, or official operations
   - Major conflicts, incidents, or acts of violence
   - Numerical or statistical claims
   - Cited studies, experts, or formal reports
   - Scientific or medical concepts
   - Theories, models, or conceptual frameworks (e.g., Hilbert space, geometric unity, string theory)
   - Religious or philosophical texts, figures, or doctrines
   - Secret societies, esoteric beliefs, or occult references

2. Write a one-sentence `SemanticSummary` that captures the **claim or concept behind the flagged items**. Use literal, factual language. The sentence must be understandable on its own and suitable for semantic similarity comparison.

RULES:
- Extract only from the Transcript — Context is only for disambiguation.
- Copy exact wording — no paraphrasing or interpretation in the Flags.
- The SemanticSummary must not include conversational filler or hedging.
- Do not include markdown, explanations, or comments.
- If there are no valid flags, return an empty list for Flags: [] and an empty string for SemanticSummary: ""

OUTPUT (Return valid Python literals):
Flags: list[str] — must be a valid Python list of quoted strings or an empty list []
SemanticSummary: str — must be a single Python string (quoted) or an empty string
""".strip()