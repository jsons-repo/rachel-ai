# src/rachel/clients/transcription/base.py
from abc import ABC, abstractmethod
from typing import List
from rachel.core.model import RawTranscriptSegment

class TranscriptionBackend(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, chunk_offset: float, started_at: float) -> List[RawTranscriptSegment]:
        pass

    def warm(self):
        """Optional: preload model weights."""
        pass  # default is no-op