# src/rachel/transcribe.py
import time
import queue
import uuid
import pyaudio
import audioop
from difflib import SequenceMatcher

from rachel.core.model import TranscriptSegment, RawTranscriptSegment
from rachel.core.types import SegmentStatus
from rachel.runtime.runtime import transcript_queue, task_queue_lock, voice_signal, pause_event, stop_signal
from rachel.runtime.threads import ManagedThread
from rachel.utils.common import debug, merge_segments_by_words_with_cutoff
from rachel.utils.print_out import print_audio_capture_started, print_audio_device_list, print_audio_config
from rachel.clients.transcription.loader import get_transcription_backend
from rachel.core.config import get_config

# Load audio config from global config
audio_cfg = get_config().audio

# Static values
FORMAT = pyaudio.paInt16

# Transcription client
backend = get_transcription_backend()

# Print configuration
print_audio_config(audio_cfg, FORMAT)

# Locals
audio_queue = queue.Queue()
frames_per_chunk = int(audio_cfg.rate * audio_cfg.chunk_duration)
overlap_frames = int(audio_cfg.rate * audio_cfg.overlap_duration)

def audio_capture():
    offset = 0.0
    pa = pyaudio.PyAudio()

    print_audio_device_list(pa)

    try:
        stream = pa.open(
            format=FORMAT,
            channels=audio_cfg.channels,
            rate=audio_cfg.rate,
            input=True,
            frames_per_buffer=audio_cfg.chunk
        )
    except Exception as e:
        print("Error opening audio stream:", e)
        return

    buf = b""
    buffer_start_time = None

    print_audio_capture_started()

    try:
        while not stop_signal.is_set():
            chunk = stream.read(audio_cfg.chunk, exception_on_overflow=False)
            rms = audioop.rms(chunk, 2)
            voice_signal["latest_volume_rms"] = rms
            if rms > audio_cfg.silence_threshold:
                voice_signal["last_non_silent_time"] = time.time()

            if buffer_start_time is None:
                buffer_start_time = time.time()

            buf += chunk

            if len(buf) >= frames_per_chunk * pa.get_sample_size(FORMAT):
                to_process = buf[:frames_per_chunk * pa.get_sample_size(FORMAT)]
                buf = buf[-overlap_frames * pa.get_sample_size(FORMAT):]
                if not pause_event.is_set():
                    audio_queue.put((offset, to_process, buffer_start_time))
                buffer_start_time = None
                offset += (audio_cfg.chunk_duration - audio_cfg.overlap_duration)

    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        pa.terminate()


def is_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold

def transcribe_worker():
    last_end_time = 0.0
    previous_text = ""

    while not stop_signal.is_set():
        if pause_event.is_set():
            time.sleep(0.2)
            continue

        try:
            item = audio_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        
        # Note: None value is the kill signal for the thread
        if item is None:
            break


        chunk_offset, audio_data, pipeline_started_at = item
        raw_segments: list[RawTranscriptSegment] = backend.transcribe(audio_data, chunk_offset, pipeline_started_at)
        if not raw_segments:
            continue

        result = merge_segments_by_words_with_cutoff(raw_segments, chunk_offset, cutoff=last_end_time)
        if not result:
            continue

        abs_start, abs_end, merged_text = result
        if is_similar(merged_text, previous_text):
            debug("[transcribe_worker] skipping near-duplicate segment")
            continue

        debug(f"[transcribe_worker] merged output text: {merged_text!r}")

        t0 = time.time()
        ts = TranscriptSegment(
            id=str(uuid.uuid4()),
            text=merged_text,
            start=abs_start,
            end=abs_end,
            created_at=t0,
            pipeline_started_at=pipeline_started_at,
            status=SegmentStatus.IN_PROGRESS
        )

        last_end_time = abs_end
        previous_text = merged_text

        with task_queue_lock:
            transcript_queue.put(ts)

def start_transcription():
    capture_thread = ManagedThread(
        target=audio_capture,
        name="AudioCapture",
        stop_signal=stop_signal,
    )
    transcribe_thread = ManagedThread(
        target=transcribe_worker,
        name="TranscribeWorker",
        stop_signal=stop_signal,
    )

    capture_thread.start()
    transcribe_thread.start()

    try:
        while not stop_signal.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received — stopping threads.")
        stop_signal.set()
    finally:
        audio_queue.put(None) 
        capture_thread.stop()
        transcribe_thread.stop()
