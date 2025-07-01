# src/rachel/api/voice_stream.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import time
import json
from rachel.runtime.runtime import voice_signal

router = APIRouter()

@router.get("/voice-stream")
async def voice_stream(request: Request):
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break

                volume = min(1.0, voice_signal["latest_volume_rms"] / 32768)
                is_speaking = time.time() - voice_signal["last_non_silent_time"] < 0.25

                yield f"data: {json.dumps({'isSpeaking': is_speaking, 'volume': volume})}\n\n"
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("🛑 voice_stream: generator cancelled")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
