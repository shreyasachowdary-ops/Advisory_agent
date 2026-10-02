"""FastAPI application — Parent/Teacher Agentic Advisor."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    HealthResponse,
    SafeguardingConfirmRequest,
)
from app.orchestrator import check_ollama_available, process_chat
from mcp_server.tools.safeguarding import submit_safeguarding_flag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Parent/Teacher Agentic Advisor",
    description="PoC advisory assistant for preschool parents and teachers",
    version=settings.kb_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

FEEDBACK_LOG = Path(settings.chroma_path).parent / "audit" / "feedback.jsonl"


@app.get("/api/health", response_model=HealthResponse)
async def health():
    ollama_ok = await check_ollama_available()
    return HealthResponse(status="ok", ollama=ollama_ok, kb_version=settings.kb_version)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(
        "Chat request: audience=%s age=%s msg_len=%d",
        request.audience,
        request.age_band,
        len(request.message),
    )
    return await process_chat(request)


@app.post("/api/feedback")
async def feedback(body: FeedbackRequest):
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rating": body.rating,
    }
    with open(FEEDBACK_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    return {"status": "recorded"}


@app.post("/api/safeguarding/confirm")
async def safeguarding_confirm(body: SafeguardingConfirmRequest):
    if not body.user_confirmed:
        raise HTTPException(
            status_code=400,
            detail="user_confirmed must be true to submit a safeguarding flag",
        )
    result = submit_safeguarding_flag(
        category=body.category,
        severity=body.severity,
        user_summary=body.user_summary,
        user_confirmed=True,
    )
    return result
