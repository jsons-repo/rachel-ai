# src/rachel/emit.py
import time
import json
from queue import Empty
from dataclasses import asdict
from rachel.core.model import ShallowTranscriptContext
from rachel.core.types import StreamResponse, SegmentStatus
from rachel.runtime.runtime import (
    shallow_queue_results,
    deep_queue_results,
    api_output_queue,
    archive_path,
    transcript_archive,
    transcript_archive_lock,
    stop_signal
)
from rachel.utils.common import debug


def serialize_segment_for_fe(sc: ShallowTranscriptContext) -> StreamResponse:
    return StreamResponse(
        id=sc.current.id,
        transcript=sc.current.text.strip(),
        start=round(sc.start or 0.0, 2),
        end=round(sc.end or 0.0, 2),
        latency=round(time.time() - getattr(sc.current, "created_at", time.time()), 2),
        last_updated=sc.current.last_updated,
        duration=round((sc.end or 0.0) - (sc.start or 0.0), 2),
        created_at=sc.current.created_at,
        pipeline_started_at=sc.current.pipeline_started_at,
        flags=[asdict(f) for f in (sc.current.flags or [])] or None,
        source="deep" if any(f.source == "deep" for f in (sc.current.flags or [])) else "shallow",
        status=sc.current.status if hasattr(sc.current, "status") else SegmentStatus.IN_PROGRESS
    )

def archive_and_emit():
    while not stop_signal.is_set():
        combined = []

        # Drain shallow queue
        try:
            while True:
                combined.append(shallow_queue_results.get_nowait())
        except Empty:
            pass

        # Drain deep queue
        try:
            while True:
                combined.append(deep_queue_results.get_nowait())
        except Empty:
            pass

        combined.sort(key=lambda x: x.start or 0)

        for sc in combined:
            final_output = serialize_segment_for_fe(sc)

            with transcript_archive_lock:
                transcript_archive[sc.current.id] = sc.current
                with open(archive_path, "w") as f:
                    json.dump([asdict(seg) for seg in transcript_archive.values()], f, indent=2)

            api_output_queue.put(final_output)
        time.sleep(0.05)

