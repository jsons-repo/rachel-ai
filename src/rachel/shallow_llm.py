from queue import Empty
from rachel.core.model import ShallowTranscriptContext, TranscriptSegment, Flag, FlagSource, ExitReason
from rachel.core.types import SegmentStatus
from rachel.clients.shallow.loader import get_shallow_llm
from rachel.semantic_filter import SemanticFilter
from rachel.runtime.runtime import (
    deep_queue,
    shallow_queue_results,
    transcript_queue,
    context_window,
    deep_context_window,
    stop_signal,
)
from rachel.utils.common import debug, parse_shallow_output
from rachel.utils.print_out import (
    print_shallow_config,
    print_shallow_prompt,
    print_flags_detected,
    print_no_flags,
    print_shallow_outputs
)
from .utils.prompts import (
    generate_shallow_prompt,
    shallow_to_prompt_context,
)
from .core.config import get_config

shallow_cfg = get_config().model.shallow_LLM
summarization_cfg = get_config().summarization
print_shallow_config(shallow_cfg)

# Cilents
llm = get_shallow_llm()
semantic_filter = SemanticFilter()


def process_segment(segment: TranscriptSegment):
    shallow_context = ShallowTranscriptContext(
        current=segment,
        context=list(context_window)
    )

    # Note: offload to /stream immediately and continue to enrich; FE will merge/dedupe via id
    shallow_queue_results.put(shallow_context)

    sc = shallow_to_prompt_context(shallow_context)
    prompt = generate_shallow_prompt(sc)

    print_shallow_prompt(prompt)

    raw_llm_output = llm.generate(prompt)
    parsed_flag_output, semantic_summary = parse_shallow_output(raw_llm_output)
    print_shallow_outputs(raw_llm_output, parsed_flag_output, semantic_summary)

    if parsed_flag_output:

        print_flags_detected(parsed_flag_output)

        flag = Flag(
            id=f"{segment.id}_shallow",
            matches=parsed_flag_output,
            severity=0.0,
            source=FlagSource.SHALLOW,
            category=None,
            source_prompt=prompt,
            summary=None,
            text=None,
            semantic_summary=semantic_summary,
        )
        segment.status = SegmentStatus.FLAGGED
        segment.flags = [flag]

        # Note: We're not spamming the queues with the same thing; each flag data is different.
        shallow_queue_results.put(ShallowTranscriptContext(current=segment, context=list(context_window)))

        if not semantic_filter.is_duplicate(semantic_summary):
            deep_queue.put(ShallowTranscriptContext(current=segment, context=list(deep_context_window)))
        else:
            segment.flags[0].exit_reason = ExitReason.DUPLICATE
            segment.status = SegmentStatus.COMPLETE
            shallow_queue_results.put(ShallowTranscriptContext(current=segment, context=list(context_window)))

    else:
        print_no_flags()
        segment.status = SegmentStatus.COMPLETE
        shallow_queue_results.put(shallow_context)

    context_window.append(segment)
    deep_context_window.append(segment)


def start_summarization():
    while not stop_signal.is_set():
        try:
            item = transcript_queue.get(timeout=0.1)
        except Empty:
            continue

        segments = item if isinstance(item, list) else [item]
        for seg in segments:
            process_segment(seg)
