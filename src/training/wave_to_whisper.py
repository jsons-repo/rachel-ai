# src/training/wave_to_whisper.py

import argparse
import os
import json
import wave
import io
import subprocess
import tempfile
from typing import List, Dict
from dataclasses import asdict
from rachel.clients.transcription.loader import get_transcription_backend
from rachel.core.model import RawTranscriptSegment
from rachel.core.config import get_config
from training.utils.common import derive_output_path

# Transcription client
backend = get_transcription_backend()

def ensure_wav_format(input_path: str) -> str:
    if input_path.lower().endswith(".wav"):
        return input_path

    print(f"🔄  Converting {input_path} to WAV...")

    tmp_wav = tempfile.mktemp(suffix=".wav")
    result = subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1",
        tmp_wav
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(result.stderr.decode())
        raise RuntimeError("ffmpeg conversion failed.")

    return tmp_wav

def chunk_audio(wav_path: str) -> List[bytes]:
    cfg = get_config()
    audio_cfg = cfg.audio

    with wave.open(wav_path, 'rb') as wf:
        frame_width = wf.getsampwidth()
        total_frames = wf.getnframes()
        audio = wf.readframes(total_frames)

        chunk_frames = int(audio_cfg.rate * audio_cfg.chunk_duration)
        overlap_frames = int(audio_cfg.rate * audio_cfg.overlap_duration)
        step = chunk_frames - overlap_frames

        chunks = []
        for start in range(0, total_frames, step):
            end = min(start + chunk_frames, total_frames)
            chunk_data = audio[start * frame_width * audio_cfg.channels:end * frame_width * audio_cfg.channels]

            with io.BytesIO() as buffer:
                with wave.open(buffer, 'wb') as wf_out:
                    wf_out.setnchannels(audio_cfg.channels)
                    wf_out.setsampwidth(frame_width)
                    wf_out.setframerate(audio_cfg.rate)
                    wf_out.writeframes(chunk_data)
                chunks.append(buffer.getvalue())

        return chunks



def transcribe_wav_to_segments(wav_path: str) -> list[RawTranscriptSegment]:
    audio_cfg = get_config().audio

    offset = 0.0
    all_segments = []

    for chunk in chunk_audio(wav_path):
        segments = backend.transcribe(chunk, offset, started_at=offset)

        for seg in segments:
            print(f"transcribed: {seg.text}")  # optional

        all_segments.extend(segments)
        offset += (audio_cfg.chunk_duration - audio_cfg.overlap_duration)

    return all_segments




def save_segments_to_json(segments: List[RawTranscriptSegment], output_path: str):
    with open(output_path, 'w') as f:
        json.dump([asdict(s) for s in segments], f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Transcribe a WAV file and save segments to JSON.")
    parser.add_argument("path_to_wav", help="Path to input WAV file")
    args = parser.parse_args()

    if not os.path.exists(args.path_to_wav):
        raise FileNotFoundError(f"WAV file not found: {args.path_to_wav}")

    print(f"📥 Transcribing: {args.path_to_wav}")
    wav_input = ensure_wav_format(args.path_to_wav)
    segments = transcribe_wav_to_segments(wav_input)

    output_path = derive_output_path(args.path_to_wav)
    save_segments_to_json(segments, output_path)

    print(f"✅ Segments saved to: {output_path}")


if __name__ == "__main__":
    main()
