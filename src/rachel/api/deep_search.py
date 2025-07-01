from fastapi import APIRouter
import time
import json
from rachel.core.types import DeepSearchRequest, DeepSearchResponse
from rachel.core.config import get_config
from rachel.utils.prompts import generate_deepsearch_prompt
from rachel.runtime.runtime import transcript_archive, transcript_archive_lock
from rachel.clients.deep.loader import get_deep_llm

router = APIRouter()
cfg = get_config()
client = get_deep_llm()

@router.post(
    "/deepsearch",
    response_model=DeepSearchResponse,
    response_description="Structured deep analysis of the given segment."
)
async def deepsearch(req: DeepSearchRequest):
    try:
        prompt = generate_deepsearch_prompt(segment_id=req.segment_id)
        if not prompt:
            return {"error": "Unable to generate prompt from archive."}

        start_time = time.time()
        response_text = client.send(prompt)
        duration = round(time.time() - start_time, 2)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "error": "Model returned invalid JSON.",
                "raw": response_text
            }

        parsed["query_duration"] = duration

        with transcript_archive_lock:
            segment = transcript_archive.get(req.segment_id)
            if segment and segment.flags:
                segment.flags[-1].deep_search = response_text

        return parsed

    except Exception as e:
        print("❌ Error during DeepSearch:", e)
        return {"error": str(e)}
