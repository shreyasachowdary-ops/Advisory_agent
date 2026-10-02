"""System prompts and response formatting."""

from app.models import SourceCitation

SYSTEM_PROMPT = """You are a Parent/Teacher Advisor for preschool children ages 2–5.

ROLE:
- Provide general, evidence-aligned educational guidance — NOT diagnosis, counselling, or medical advice.
- Be calm, non-judgmental, and culturally respectful. Never label or shame a child.
- Distinguish observed behaviour from assumed intent.
- Suggest small, observable, play-based interventions with review dates.
- Use retrieved knowledge sources when available; say when evidence is insufficient.
- Never recommend punishment, shaming, exclusion, or concealing concerns.
- Preserve parent–teacher partnership; do not blame or take sides.
- Never invent school policy, contacts, research, or student facts.
- Request confirmation before any external-facing action.

RESPONSE FORMAT (for normal queries):
1. Brief acknowledgement
2. What may help this week (2–4 concrete, play-based, age-appropriate actions)
3. What to observe / discuss with the other adult
4. When to seek extra support
5. Sources used (cite retrieved passages)

Keep language simple and practical. Target audience may be a parent or teacher."""

ESCALATION_TEMPLATES = {
    "urgent": (
        "This situation needs immediate attention from a safeguarding professional. "
        "Please do not rely on this chat for next steps."
    ),
    "referral": (
        "Ongoing or specialised concerns are best discussed with a teacher, counsellor, "
        "or health professional. General tips cannot replace that support."
    ),
}


def format_normal_response(
    acknowledgement: str,
    actions: list[str],
    observe: str,
    extra_support: str,
    sources: list[SourceCitation],
) -> str:
    """Format a structured normal response."""
    lines = [acknowledgement.strip(), "", "**What may help this week:**"]
    for i, action in enumerate(actions[:4], 1):
        lines.append(f"{i}. {action.strip()}")

    lines.extend(["", "**What to observe / discuss with the other adult:**", observe.strip()])
    lines.extend(["", "**When to seek extra support:**", extra_support.strip()])

    if sources:
        lines.extend(["", "**Sources used:**"])
        for src in sources:
            lines.append(f"- {src.title} ({src.url})")

    return "\n".join(lines)


def build_fallback_response(
    message: str,
    actions: list[str],
    sources: list[SourceCitation],
    follow_up: str,
) -> str:
    """Template response when Ollama is unavailable."""
    return format_normal_response(
        acknowledgement=(
            f"I hear you're asking about: \"{message[:120]}{'...' if len(message) > 120 else ''}\". "
            "Here is practical guidance based on approved early-childhood resources."
        ),
        actions=actions,
        observe="Notice what happens before, during, and after the situation. Share brief, factual observations with the other adult.",
        extra_support=(
            "If the concern persists for several weeks, affects daily functioning, or you feel worried "
            "about the child's wellbeing, speak with your school's counsellor or paediatrician."
        ),
        sources=sources,
    ) + (f"\n\n**Follow-up question:** {follow_up}" if follow_up else "")
