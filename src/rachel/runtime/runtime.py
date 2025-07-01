# src/rachel/runtime/runtime.py

import os
import queue
import threading
import time
from collections import deque
from threading import Lock

from rachel.core.config import get_config
from rachel.core.model import TranscriptSegment

# Load summarization and deep model config
cfg = get_config()
summarization_cfg = cfg.summarization
deep_llm_cfg = cfg.model.deep_LLM
semantic_cfg = cfg.model.semantic

# App-wide coordination signals
pause_event = threading.Event()
pause_event.set()  # Start in paused state
stop_signal = threading.Event()

# Signal for real-time audio activity
voice_signal = {
    "last_non_silent_time": time.time(),
    "latest_volume_rms": 0.0,
}

# Save to disk
transcript_archive: dict[str, TranscriptSegment] = {}
ARCHIVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "transcripts"))
os.makedirs(ARCHIVE_DIR, exist_ok=True)
archive_path = os.path.join(ARCHIVE_DIR, "transcript_archive.json")

# Locks for task queues to avoid race conditions
task_queue_lock = Lock()
deep_queue_lock = Lock()
semantic_lock = Lock()
deep_queue_results_lock = Lock()
transcript_archive_lock = Lock()

# Shared queues
api_output_queue = queue.Queue()
deep_queue = queue.Queue()
deep_queue_results = queue.Queue()
shallow_queue_results = queue.Queue()
transcript_queue = queue.Queue()

# Shared context windows
flag_history = deque(maxlen=50)
context_window = deque(maxlen=summarization_cfg.shallow_context_window)
deep_context_window = deque(maxlen=summarization_cfg.deep_context_window)
recent_flags_window = deque(maxlen=deep_llm_cfg.recentFlagSize)
semantic_window = deque(maxlen=semantic_cfg.context_limit)
