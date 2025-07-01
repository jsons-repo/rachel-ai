# src/rachel/core/model.py

import time
from dataclasses import dataclass, field
from typing import List, Optional
from rachel.core.types import FlagSource, FlagCategory, ExitReason, SegmentStatus

@dataclass
class RawTranscriptWord:
    start: float
    end: float
    text: str
    confidence: Optional[float] = None  # Optional: only some models support it


@dataclass
class RawTranscriptSegment:
    start: float
    end: float
    text: str

    words: Optional[List[RawTranscriptWord]] = None     # Optional: detailed word timings
    speaker: Optional[str] = None                       # Optional: for diarization
    confidence: Optional[float] = None                  # Optional: avg segment confidence
    language: Optional[str] = None                      # Optional: language ID
    raw_backend_data: Optional[dict] = None             # Optional: original model payload

@dataclass
class Flag:
    id: str
    matches: List[str]      
    source: FlagSource       
    severity: float = 0.0
    category: Optional[FlagCategory] = None
    exit_reason: Optional[ExitReason] = None
    source_prompt: Optional[str] = None
    summary: Optional[str] = None
    text: Optional[str] = None
    deep_search: Optional[str] = None
    semantic_summary: Optional[str] = None

@dataclass
class TranscriptSegment:
    id: str
    text: str
    start: float
    end: float
    flags: Optional[List["Flag"]] = None
    created_at: float = field(default_factory=time.time)
    pipeline_started_at: Optional[float] = None
    status: SegmentStatus = SegmentStatus.IN_PROGRESS
    last_updated: float = field(default_factory=time.time)

    def __setattr__(self, name, value):
        tracked_fields = {'status', 'flags'}
        current_value = getattr(self, name, None)

        # only update if value is actually different
        if name in tracked_fields and current_value != value:
            super().__setattr__('last_updated', time.time())

        super().__setattr__(name, value)

@dataclass
class ShallowTranscriptContext:
    current: TranscriptSegment
    context: List[TranscriptSegment] = field(default_factory=list)
    deep_context: List[TranscriptSegment] = field(default_factory=list)

    @property
    def start(self) -> Optional[float]:
        return self.current.start

    @property
    def end(self) -> Optional[float]:
        return self.current.end

    @property
    def text(self) -> Optional[str]:
        return self.current.text

    @property
    def context_flags(self) -> List[Flag]:
        """Return all flags from context segments."""
        return [
            flag
            for seg in self.context
            for flag in (seg.flags or [])
        ]


