# rachel/core/types.py--

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from enum import Enum

# ----------------------------------------
# 🔹 ENUMS
# ----------------------------------------

class FlagSource(str, Enum):
    SHALLOW = "shallow"
    DEEP = "deep"
    USER = "user"

class FlagCategory(str, Enum):
    PERSON = "person"
    PLACE = "place"
    CLAIM = "claim"
    ORG = "org"
    EVENT = "event"

class ExitReason(str, Enum):
    NONE = "none"
    DUPLICATE = "duplicate"
    CONFUSING = "confusing"
    INSUBSTANTIAL = "insubstantial"

class SegmentStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FLAGGED = "flagged"
    COMPLETE = "complete"


# ----------------------------------------
# 🔹 FLAG + SEGMENT PAYLOAD
# ----------------------------------------

class FlagDict(BaseModel):
    id: str = Field(..., description="Unique identifier for the flag")
    matches: List[str] = Field(..., description="List of verbatim strings that triggered the flag")
    severity: float = Field(..., description="Severity score of the flag (typically 0.0–1.0)")
    source: FlagSource = Field(..., description="Source of the flag (e.g. 'shallow', 'deep', or 'user')")
    summary: Optional[str] = Field(None, description="High-level summary or interpretation of the flag")
    text: Optional[str] = Field(None, description="Full flagged text content")
    category: Optional[FlagCategory] = Field(None, description="Optional category like 'claim', 'person', 'event'")
    source_prompt: Optional[str] = Field(None, description="The prompt used to generate this flag, if applicable")
    exit_reason: Optional[ExitReason] = Field(None, description="Reason this flag was filtered or rejected, if applicable")
    deep_search: Optional[str] = Field(None, description="The deep search result (if user requested)")


class StreamResponse(BaseModel):
    id: str = Field(..., title="Segment ID", description="Unique identifier for the segment in the transcript stream")
    transcript: str = Field(..., title="Transcript Text", description="Cleaned transcript text from the segment")
    start: float = Field(..., title="Start Time", description="Start time of the segment in seconds")
    end: float = Field(..., title="End Time", description="End time of the segment in seconds")
    latency: float = Field(..., title="Latency", description="Total processing delay in seconds")
    last_updated: float = Field(..., title="Last Updated Timestamp", description="Unix timestamp of last substantive mutation to this segment")
    duration: float = Field(..., title="Duration", description="Duration of the segment")
    created_at: float = Field(..., title="Created Timestamp", description="Unix timestamp of segment creation")
    pipeline_started_at: float = Field(..., title="Pipeline Created Timestamp", description="Unix timestamp of pipeline input")
    flags: Optional[List[FlagDict]] = Field(None, title="Flag List", description="Flags attached to this segment")
    status: SegmentStatus = Field(..., title="Segment Status", description="Current pipeline status of this segment")
    source: Optional[str] = Field(None, title="Source Stage", description="Stage that triggered this emission (e.g., 'transcribe', 'shallow', 'deep')")

# ----------------------------------------
# 🔹 DEEP SEARCH REQUEST/RESPONSE
# ----------------------------------------

class DeepSearchRequest(BaseModel):
    segment_id: str = Field(..., title="Segment ID", description="The unique ID of the transcript segment")


class DeepSearchResponse(BaseModel):
    topic: str = Field(..., title="Flagged Topic", description="The exact phrase or phrases being investigated")
    summary: str = Field(..., description="High-level factual summary of the topic")
    key_figures: List[str] = Field(..., description="Notable people involved in or connected to the topic")
    timeline: List[str] = Field(..., description="Chronological list of dated events")
    controversy: str = Field(..., description="What makes the topic contested or confusing")
    evidence: str = Field(..., description="Primary sources or counter-evidence")
    query_duration: float = Field(..., description="Total time (in seconds) for the GPT query")


# ----------------------------------------
# 🔹 USER SEARCH REQUEST/RESPONSE
# ----------------------------------------

class UserSearchRequest(BaseModel):
    segment_id: str = Field(..., title="Segment ID", description="The unique ID of the transcript segment")
    selected_text: str = Field(..., title="Selected Text", description="The exact transcript excerpt flagged by the user")
    query: Optional[str] = Field("", title="User Query", description="Optional freeform prompt or clarification from the user")

class UserSearchResponse(BaseModel):
    headline: str = Field(..., description="A concise title summarizing the core issue")
    body: str = Field(..., description="A full explanation with relevant context and evidence")
    key_figures: List[str] = Field(..., description="Names of important people or entities relevant to the topic")
    timeline: List[str] = Field(..., description="Chronological list of events with dates")
    query_duration: float = Field(..., description="Total time in seconds spent generating the response")


# ----------------------------------------
# 🔹 SYSTEM METRICS RESPONSE
# ----------------------------------------

class QueueLengths(BaseModel):
    transcript: int = Field(..., description="Number of items in the transcript queue")
    shallow_results: int = Field(..., description="Number of items in the shallow analysis result queue")
    deep_queue: int = Field(..., description="Number of items waiting for deep analysis")
    deep_results: int = Field(..., description="Number of deep analysis results ready for streaming")


class MetricsResponse(BaseModel):
    cpu: float = Field(..., description="CPU usage as a percentage", example=82.4)
    ram: float = Field(..., description="RAM usage as a percentage", example=74.1)
    gpu: Optional[float] = Field(None, description="GPU usage as a percentage (if available)", example=43.2)
    queues: QueueLengths = Field(..., description="Current lengths of processing queues")
    segments_processed: int = Field(..., description="Total number of transcript segments processed")
    timestamp: float = Field(..., description="Unix timestamp when this snapshot was taken", example=1715880003.84)

# ----------------------------------------
# 🔹 VOICE SIGNAL RESPONSE
# ----------------------------------------

class VoiceSignalResponse(BaseModel):
    is_speaking: bool = Field(..., description="Whether the speaker has spoken within the last .25 seconds")
    volume: float = Field(..., description="Current audio volume as a normalized float between 0.0 (silence) and 1.0 (max)")
