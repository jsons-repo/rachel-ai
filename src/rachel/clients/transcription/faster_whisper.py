# src/rachel/clients/transcription/faster_whisper.py

import os
import time
import numpy as np
from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download
from typing import List, Optional

from .base import TranscriptionBackend
from rachel.core.model import RawTranscriptSegment, RawTranscriptWord
from rachel.core.config import get_config
from rachel.utils.file_system import get_model_subdir_path, assert_model_path_exists
from rachel.utils.hardware import resolve_device_and_type
from rachel.utils.metrics import record_metrics


class FasterWhisperBackend(TranscriptionBackend):
    def __init__(self):
        cfg = get_config()
        tcfg = cfg.model.transcription

        self.model_path = get_model_subdir_path(cfg.transcription_root, tcfg.backend)

        print(f"📦 Downloading or loading Faster-Whisper model from: {tcfg.repo} to: {self.model_path}")
        snapshot_download(
            repo_id=tcfg.repo,
            local_dir=self.model_path,
            use_auth_token=cfg.hf_token
        )
        assert_model_path_exists(self.model_path)

        device, compute_type = resolve_device_and_type(tcfg.device, tcfg.compute_type)
        print(f"🎙️ Initializing Faster-Whisper with device={device}, compute_type={compute_type}")

        self.model = WhisperModel(
            self.model_path,
            device=device,
            compute_type=compute_type,
            cpu_threads=os.cpu_count() // 2 if device == "cpu" else 1,
            num_workers=1
        )

    def transcribe(
        self,
        audio_bytes: bytes,
        chunk_offset: Optional[float],
        started_at: Optional[float]
    ) -> List[RawTranscriptSegment]:
        cfg = get_config()
        tcfg = cfg.model.transcription

        t0 = time.time()

        # Convert PCM bytes to float32
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        segments_gen, info = self.model.transcribe(
            audio_array,
            beam_size=tcfg.beam_size,
            word_timestamps=True,
            language=tcfg.lang,
            temperature=tcfg.temp,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500,
                "speech_pad_ms": 400
            }
        )

        record_metrics(tcfg.backend, t0, audio_duration=len(audio_array) / cfg.audio.rate)

        results = []
        for segment in segments_gen:
            words = []
            if hasattr(segment, 'words') and segment.words:
                words = [
                    RawTranscriptWord(
                        start=w.start,
                        end=w.end,
                        text=w.word,
                        confidence=getattr(w, 'probability', None)
                    ) for w in segment.words
                ]

            results.append(
                RawTranscriptSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip(),
                    words=words,
                    confidence=getattr(segment, 'avg_logprob', None),
                    language=getattr(info, 'language', tcfg.lang)
                )
            )

        return results
