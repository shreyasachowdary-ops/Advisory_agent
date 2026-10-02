"""Ollama + MCP tool orchestration."""

import json
import logging
import re
from typing import Any

import httpx

from app.config import settings
from app.models import ChatRequest, ChatResponse, RiskLevel, SourceCitation
from app.prompts import SYSTEM_PROMPT, build_fallback_response, format_normal_response
from app.safety import classify_safety
from mcp_server.tools.activity_plan import create_activity_plan
from mcp_server.tools.search_knowledge import search_knowledge

logger = logging.getLogger(__name__)

ACTIVITY_PLAN_KEYWORDS = re.compile(
    r"\b(activity\s+plan|5[- ]?day|five[- ]?day|turn[- ]?taking\s+plan|weekly\s+plan)\b",
    re.I,
)

FOLLOW_UP_TEMPLATES = {
    "routines": "How consistent is your morning routine right now?",
    "behaviour": "When does this behaviour usually happen — mornings, transitions, or playtime?",
    "communication": "Have you had a chance to share observations with the other adult yet?",
    "play": "What kinds of play does the child enjoy most?",
    "default": "Can you tell me a bit more about what you've tried so far?",
}


async def check_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


def _snippets_to_sources(snippets: list[dict[str, Any]]) -> list[SourceCitation]:
    return [
        SourceCitation(
            title=s.get("title", "Source"),
            url=s.get("url", ""),
            chunk_id=s.get("chunk_id", ""),
        )
        for s in snippets
    ]


def _infer_topic(message: str) -> str:
    lower = message.lower()
    if any(w in lower for w in ("routine", "morning", "bedtime", "drop-off", "drop off")):
        return "routines"
    if any(w in lower for w in ("share", "tantrum", "bite", "push", "hit", "anxiety", "cry")):
        return "behaviour"
    if any(w in lower for w in ("parent", "teacher", "communicat", "meeting")):
        return "communication"
    if any(w in lower for w in ("play", "activity", "learn")):
        return "play"
    return "default"


def _extract_actions_from_snippets(snippets: list[dict[str, Any]], message: str) -> list[str]:
    actions: list[str] = []
    for s in snippets[:3]:
        text = s.get("text", "")
        sentences = [sent.strip() for sent in re.split(r"[.!?]", text) if len(sent.strip()) > 20]
        if sentences:
            actions.append(sentences[0] + ".")
    if len(actions) < 2:
        actions.extend(
            [
                "Use a simple visual schedule so the child can see what happens next.",
                "Praise small efforts with specific language: 'You put on your shoes — well done!'",
                "Keep transitions short and predictable; give a 2-minute warning before changes.",
            ]
        )
    return actions[:4]


def _detect_activity_plan_request(message: str) -> str | None:
    """Return plan goal only when user explicitly requests a plan."""
    lower = message.lower()
    wants_plan = bool(
        ACTIVITY_PLAN_KEYWORDS.search(message)
        or re.search(r"\b(create|make|generate|need|give me)\b.*\bplan\b", lower)
        or re.search(r"\bplan\b.*\b(for|about)\b", lower)
    )
    if not wants_plan:
        return None

    if "turn" in lower and ("taking" in lower or "turns" in lower):
        return "turn_taking_during_play"
    if "morning" in lower and "routine" in lower:
        return "morning_routine"
    if "shar" in lower:
        return "sharing_toys"
    if "separation" in lower or "drop-off" in lower or "drop off" in lower:
        return "separation_anxiety"
    return "turn_taking_during_play"


async def _call_ollama(messages: list[dict[str, str]], tools: list[dict] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": settings.ollama_chat_model,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()


OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search curated early-childhood knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "audience": {"type": "string"},
                    "age_band": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_activity_plan",
            "description": "Generate a deterministic play-based activity plan",
            "parameters": {
                "type": "object",
                "properties": {
                    "age_band": {"type": "string"},
                    "goal": {"type": "string"},
                    "available_minutes_per_day": {"type": "integer"},
                    "days": {"type": "integer"},
                    "setting": {"type": "string"},
                },
                "required": ["age_band", "goal"],
            },
        },
    },
]


def _execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "search_knowledge":
        return search_knowledge(**args)
    if name == "create_activity_plan":
        return create_activity_plan(**args)
    return {"error": f"Unknown tool: {name}"}


async def process_chat(request: ChatRequest, use_ollama: bool = True) -> ChatResponse:
    """Main chat orchestration pipeline."""
    safety = classify_safety(request.message)

    if safety.risk_level == RiskLevel.URGENT:
        return ChatResponse(
            answer=safety.escalation_message or "",
            risk_level=RiskLevel.URGENT,
            sources=[],
            requires_human_review=True,
        )

    if safety.risk_level == RiskLevel.REFERRAL:
        return ChatResponse(
            answer=safety.escalation_message or "",
            risk_level=RiskLevel.REFERRAL,
            sources=[],
            suggested_follow_up="Would you like general support ideas while you arrange a professional conversation?",
            requires_human_review=True,
        )

    # Normal flow — retrieve knowledge
    kb_result = search_knowledge(
        query=request.message,
        audience=request.audience.value,
        age_band=request.age_band.value,
        max_results=4,
    )
    snippets = kb_result.get("results", [])
    sources = _snippets_to_sources(snippets)
    topic = _infer_topic(request.message)
    follow_up = FOLLOW_UP_TEMPLATES.get(topic, FOLLOW_UP_TEMPLATES["default"])

    # Activity plan request
    plan_goal = _detect_activity_plan_request(request.message)
    if plan_goal:
        setting = "classroom" if request.audience.value == "teacher" else "home"
        plan = create_activity_plan(
            age_band=request.age_band.value,
            goal=plan_goal,
            available_minutes_per_day=15,
            days=5,
            setting=setting,
        )
        plan_text = _format_activity_plan(plan)
        return ChatResponse(
            answer=plan_text,
            risk_level=RiskLevel.NORMAL,
            sources=sources,
            suggested_follow_up="Would you like to adjust the plan for your setting?",
            requires_human_review=False,
        )

    ollama_ok = use_ollama and await check_ollama_available()

    if ollama_ok:
        try:
            answer = await _generate_with_ollama(request, snippets)
            return ChatResponse(
                answer=answer,
                risk_level=RiskLevel.NORMAL,
                sources=sources,
                suggested_follow_up=follow_up,
                requires_human_review=False,
            )
        except Exception as exc:
            logger.warning("Ollama generation failed, using fallback: %s", exc)

    # Fallback mode
    actions = _extract_actions_from_snippets(snippets, request.message)
    answer = build_fallback_response(request.message, actions, sources, follow_up)
    return ChatResponse(
        answer=answer,
        risk_level=RiskLevel.NORMAL,
        sources=sources,
        suggested_follow_up=follow_up,
        requires_human_review=False,
    )


def _format_activity_plan(plan: dict[str, Any]) -> str:
    lines = [
        f"**{plan['title']}** ({plan['age_band']}, {plan['setting']})",
        "",
        f"**Setup:** {plan['setup']}",
        "",
        "**Adult language to model:**",
    ]
    for phrase in plan["adult_language"]:
        lines.append(f"- \"{phrase}\"")
    lines.append("")
    lines.append("**Daily plan:**")
    for day in plan["daily_plan"]:
        lines.append(f"- Day {day['day']} ({day['duration_minutes']} min): {day['activity']}")
    lines.append("")
    lines.append(f"**What to observe:** {plan['observation_prompt']}")
    lines.append("")
    lines.append("_This plan is editable — adapt materials and timing to your child or classroom._")
    return "\n".join(lines)


async def _generate_with_ollama(request: ChatRequest, snippets: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        f"[{s.get('title', 'Source')}]: {s.get('text', '')}" for s in snippets[:4]
    )
    user_content = (
        f"Audience: {request.audience.value}\n"
        f"Age band: {request.age_band.value}\n"
        f"Question: {request.message}\n\n"
        f"Retrieved sources:\n{context if context else 'No sources retrieved.'}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    response = await _call_ollama(messages, tools=OLLAMA_TOOLS)
    msg = response.get("message", {})

    # Handle tool calls if present
    tool_calls = msg.get("tool_calls") or []
    if tool_calls:
        messages.append(msg)
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            result = _execute_tool(name, args)
            messages.append({"role": "tool", "content": json.dumps(result)})

        response = await _call_ollama(messages)
        msg = response.get("message", {})

    content = msg.get("content", "")
    if content:
        return content

    # If Ollama returns empty, use template
    actions = _extract_actions_from_snippets(snippets, request.message)
    return format_normal_response(
        acknowledgement="Here is guidance based on approved early-childhood resources.",
        actions=actions,
        observe="Notice patterns before, during, and after the situation.",
        extra_support="Speak with your school counsellor if concerns persist beyond a few weeks.",
        sources=_snippets_to_sources(snippets),
    )


async def process_chat_mock(request: ChatRequest) -> ChatResponse:
    """Mock response for initial frontend integration testing."""
    safety = classify_safety(request.message)
    if safety.risk_level != RiskLevel.NORMAL:
        return ChatResponse(
            answer=safety.escalation_message or "",
            risk_level=safety.risk_level,
            sources=[],
            requires_human_review=True,
        )

    return ChatResponse(
        answer=(
            f"Thank you for your question about your {request.age_band.value.replace('_', ' ')} old. "
            "This is a mock response — the full advisor pipeline is active. "
            "Try asking about morning routines, turn-taking, or separation at drop-off."
        ),
        risk_level=RiskLevel.NORMAL,
        sources=[
            SourceCitation(
                title="CDC Positive Parenting Tips",
                url="https://www.cdc.gov/child-development/positive-parenting-tips/index.html",
                chunk_id="kb-mock-001",
            )
        ],
        suggested_follow_up="How long has this been happening?",
        requires_human_review=False,
    )
