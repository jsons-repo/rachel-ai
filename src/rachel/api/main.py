# src/rachel/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from contextlib import asynccontextmanager

from rachel.api.stream import router as stream_router
from rachel.api.deep_search import router as deepsearch_router
from rachel.api.metrics import router as metrics_router
from rachel.api.voice_stream import router as voice_stream_router
from rachel.api.user_search import router as user_search_router
from rachel.api.start_stop import router as start_stop_router
from rachel.core.config import get_config
from rachel.transcription import start_transcription
from rachel.shallow_llm import start_summarization
from rachel.deep_llm import process_deep_queue
from rachel.emit import archive_and_emit
from rachel.runtime.runtime import stop_signal
from rachel.runtime.threads import ManagedThread

config = get_config()
fe_config = config.network.fe
be_config = config.network.be

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ [FastAPI] Lifespan startup")
    managed_threads = [
        ManagedThread(target=start_transcription, name="TranscriptionThread", stop_signal=stop_signal),
        ManagedThread(target=start_summarization, name="SummarizationThread", stop_signal=stop_signal),
        ManagedThread(target=process_deep_queue, name="DeepQueueThread", stop_signal=stop_signal),
        ManagedThread(target=archive_and_emit, name="EmitThread", stop_signal=stop_signal),
    ]

    for mt in managed_threads:
        mt.start()

    try:
        yield
    finally:
        stop_signal.set()
        for mt in managed_threads:
            mt.stop(timeout=5)
        print("✅ All threads shut down cleanly.")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[f"{fe_config.protocol}://{fe_config.host}:{fe_config.port}"],
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(start_stop_router)
app.include_router(stream_router)
app.include_router(deepsearch_router)
app.include_router(metrics_router)
app.include_router(voice_stream_router)
app.include_router(user_search_router)

def main():
    print(f"🚀 Launching server at {be_config.host}:{be_config.port}")
    uvicorn.run(
        "rachel.api.main:app",
        host=be_config.host,
        port=be_config.port,
        log_level="info",
        reload=False,
    )
