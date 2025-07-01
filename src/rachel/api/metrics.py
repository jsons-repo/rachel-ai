# rachel/src/rachel/api/stream.py

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import psutil
import subprocess
import time
import json
import asyncio
from rachel.runtime.runtime import (
    transcript_archive,
    transcript_archive_lock,
    transcript_queue,
    shallow_queue_results,
    deep_queue,
    deep_queue_results,
)

router = APIRouter()

@router.get("/metrics/stream", summary="Stream system metrics for dashboard")
async def metrics_stream(request: Request):
    """
    Streams lightweight system and queue metrics over SSE for monitoring.
    Ideal for status bars or admin panels.
    """
    async def stream_metrics():
        while not await request.is_disconnected():
            try:
                # System metrics
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent

                try:
                    gpu_output = subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                        text=True
                    ).strip()
                    gpu = float(gpu_output.splitlines()[0])
                except Exception:
                    gpu = None  # Gracefully degrade

                # Queue sizes and archive stats
                with transcript_archive_lock:
                    processed = len(transcript_archive)

                payload = {
                    "cpu": cpu,
                    "ram": ram,
                    "gpu": gpu,
                    "queues": {
                        "transcript": transcript_queue.qsize(),
                        "shallow_results": shallow_queue_results.qsize(),
                        "deep_queue": deep_queue.qsize(),
                        "deep_results": deep_queue_results.qsize(),
                    },
                    "segments_processed": processed,
                    "timestamp": time.time()
                }

                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(1)

            except Exception as e:
                print("❌ Error in metrics stream:", e)
                await asyncio.sleep(1)

        print("❌ Client disconnected from /metrics/stream")

    return StreamingResponse(stream_metrics(), media_type="text/event-stream")
