from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.llm import generate_answer
from app.schemas import AskRequest, AskResponse
from app.usage import get_usage, record_usage

app = FastAPI(title="Onboard Atlas", version="0.3.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    """Liveness check. Does not call the LLM or database."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Generate an answer using Gemini with automatic fallback."""
    try:
        result = generate_answer(request.question)
        record_usage(result)
        return AskResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc


@app.get("/usage")
def usage() -> dict:
    """Return accumulated token usage and estimated API cost."""
    return get_usage()
