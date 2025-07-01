# src/rachel/api/start_stop.py
import asyncio
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import json
import time
from rachel.runtime.runtime import pause_event

router = APIRouter(prefix="/stream")

@router.post("/start")
def start_pipeline():
    pause_event.clear()
    return {"status": "started"}

@router.post("/pause")
def pause_pipeline():
    pause_event.set()
    return {"status": "paused"}

@router.get("/status")
async def stream_pipeline_status():
    async def event_generator():
        # Status
        yield {
            "event": "pipeline_state",
            "data": json.dumps({"paused": pause_event.is_set()})
        }
        # Heartbeat
        while True:
            await asyncio.sleep(5)
            yield {"event": "heartbeat", "data": "ping"}

    return EventSourceResponse(event_generator())
