# rachel/src/rachel/api/stream.py

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import queue
import json
import time
from rachel.runtime.runtime import api_output_queue
from rachel.core.types import StreamResponse
from rachel.utils.common import debug

router = APIRouter()

@router.get(
    "/stream",
    summary="Subscribe to real-time event stream",
    response_description="Stream of segment payloads over SSE",
    response_model=StreamResponse
)
async def stream_facts(request: Request):
    print("New client connected to /stream endpoint")
    loop = asyncio.get_event_loop()

    async def event_generator():
        try:
            while not await request.is_disconnected():
                try:
                    data = await loop.run_in_executor(None, lambda: api_output_queue.get(timeout=1))
                    payload = f"data: {data.json()}\n\n"
                    print("API/stream => OUT:")
                    print(payload)
                    yield payload
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print("💥 Unexpected error in SSE stream:", repr(e))
                    await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("🛑 Generator cancelled")
        finally:
            print("❌ Client disconnected from /stream")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
