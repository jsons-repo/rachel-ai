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
from rachel.api.pubsub import subscribe, unsubscribe, broadcast_to_all_clients

router = APIRouter()

# Flag to prevent duplicate background tasks
bg_task_started = False

def start_background_broadcast_loop():
    async def loop_forever():
        loop = asyncio.get_event_loop()
        print("✅ Starting background fan-out task for /stream subscribers")
        while True:
            try:
                item = await loop.run_in_executor(None, lambda: api_output_queue.get(timeout=1))
                print("🔄 Broadcasting new item to subscribers")
                broadcast_to_all_clients(item)
            except queue.Empty:
                await asyncio.sleep(0.1)
            except Exception as e:
                print("💥 Error in background broadcast loop:", repr(e))
                await asyncio.sleep(0.5)
    asyncio.create_task(loop_forever())

@router.on_event("startup")
async def startup_event():
    global bg_task_started
    if not bg_task_started:
        start_background_broadcast_loop()
        bg_task_started = True

@router.get(
    "/stream",
    summary="Subscribe to real-time event stream",
    response_description="Stream of segment payloads over SSE",
    response_model=StreamResponse
)
async def stream_facts(request: Request):
    print("🟢 New client connected to /stream endpoint")
    client_queue = subscribe()

    async def event_generator():
        try:
            while not await request.is_disconnected():
                try:
                    data = await asyncio.wait_for(client_queue.get(), timeout=1.0)
                    payload = f"data: {data.json()}\n\n"
                    print("API/stream => OUT:")
                    print(payload)
                    yield payload
                except asyncio.TimeoutError:
                    # Keep-alive comment to prevent client disconnect
                    yield ": keep-alive\n\n"
                except Exception as e:
                    print("💥 Unexpected error in SSE stream:", repr(e))
                    await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("🛑 Generator cancelled")
        finally:
            unsubscribe(client_queue)
            print("❌ Client disconnected from /stream")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
