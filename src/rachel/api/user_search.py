from fastapi import APIRouter, HTTPException
import time
import json
from rachel.core.config import get_config
from rachel.core.types import UserSearchRequest, UserSearchResponse
from rachel.runtime.runtime import transcript_archive, transcript_archive_lock
from rachel.utils.common import debug, parse_gpt_json_response
from rachel.utils.prompts import generate_user_search_prompt
from rachel.clients.deep.loader import get_deep_llm

router = APIRouter()
cfg = get_config()
client = get_deep_llm()

@router.post(
    "/user-search",
    response_model=UserSearchResponse,
    response_description="Structured user-driven deep analysis of the selected transcript section."
)
async def user_search(req: UserSearchRequest):
    try:
        prompt = generate_user_search_prompt(
            segment_id=req.segment_id,
            selected_text=req.selected_text,
            query=req.query or ""
        )
        if not prompt:
            return {"error": "Unable to generate prompt from archive."}

        debug("user-search: prompt", prompt)

        start_time = time.time()
        response_text = client.send(prompt)
        duration = round(time.time() - start_time, 2)

        try:
            parsed = parse_gpt_json_response(response_text)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Model returned invalid JSON. Raw output: {response_text}"
            )

        response = UserSearchResponse(
            headline=parsed.get("headline", ""),
            body=parsed.get("body", ""),
            key_figures=parsed.get("key_figures", []),
            timeline=parsed.get("timeline", []),
            query_duration=duration
        )

        with transcript_archive_lock:
            segment = transcript_archive.get(req.segment_id)
            if segment and segment.flags:
                segment.flags[-1].deep_search = response

        print("user-search:response:", response)
        return response

    except Exception as e:
        print("❌ Error during UserSearch:", e)
        return {"error": str(e)}
