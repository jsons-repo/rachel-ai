# src/rachel/clients/transcription/mlx.py

import os
import time
import numpy as np
import mlx_whisper
from typing import List, Optional
from huggingface_hub import snapshot_download

from rachel.core.model import RawTranscriptSegment, RawTranscriptWord
from rachel.core.config import get_config
from rachel.utils.common import debug
from rachel.utils.file_system import get_model_subdir_path, assert_model_path_exists
from rachel.runtime.metrics import record_metrics
from rachel.clients.transcription.base import TranscriptionBackend


class MlxWhisperClient(TranscriptionBackend):
    def __init__(self):
        cfg = get_config()
        tcfg = cfg.model.transcription

        model_dir = get_model_subdir_path(cfg.transcription_root, tcfg.backend)

        print(f"📦 Downloading or loading MLX Whisper model from: {tcfg.repo} to: {model_dir}")

        self.model_path = snapshot_download(
            repo_id=tcfg.repo,
            use_auth_token=cfg.hf_token,
            local_dir=model_dir
        )

        assert_model_path_exists(self.model_path)

    def transcribe(
        self,
        audio_bytes: bytes,
        chunk_offset: Optional[float],
        started_at: Optional[float]
    ) -> List[RawTranscriptSegment]:
        cfg = get_config()
        tcfg = cfg.model.transcription

        t0 = time.time()

        # Convert PCM bytes to numpy float32 array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        result = mlx_whisper.transcribe(
            audio_array,
            path_or_hf_repo=self.model_path,
            word_timestamps=tcfg.word_timestamps,
            language=tcfg.lang,
            temperature=tcfg.temp,
            fp16=True  # Always use fp16 on Metal
        )

        record_metrics(tcfg.backend, t0, audio_duration=len(audio_array) / cfg.audio.rate)

        segments = []
        for seg in result.get("segments", []):
            words = []
            if "words" in seg:
                words = [
                    RawTranscriptWord(
                        start=w["start"],
                        end=w["end"],
                        text=w["word"],
                        confidence=w.get("probability", None)
                    )
                    for w in seg["words"]
                ]

            segments.append(
                RawTranscriptSegment(
                    start=seg["start"],
                    end=seg["end"],
                    text=seg["text"].strip(),
                    words=words,
                    language=result.get("language", tcfg.lang),
                    confidence=seg.get("avg_logprob", None)
                )
            )

        return segments
