# src/rachel/clients/transcription/loader.py

from rachel.core.config import get_config

def _lazy_import_faster_whisper():
    from .faster_whisper import FasterWhisperBackend
    return FasterWhisperBackend

def _lazy_import_mlx():
    from .mlx import MlxWhisperClient
    return MlxWhisperClient


TRANSCRIPTION_BACKEND_MAP = {
    "faster-whisper": _lazy_import_faster_whisper,
    "mlx-whisper": _lazy_import_mlx,
}


def get_transcription_backend():
    backend_name = get_config().model.transcription.backend
    try:
        BackendClass = TRANSCRIPTION_BACKEND_MAP[backend_name]()
        return BackendClass()
    except KeyError:
        raise ValueError(
            f"❌ Unknown transcription backend: '{backend_name}'. "
            f"Valid options: {list(TRANSCRIPTION_BACKEND_MAP.keys())}"
        )

