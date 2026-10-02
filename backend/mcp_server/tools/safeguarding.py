"""Safeguarding flag submission — test sink only, requires confirmation."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import BACKEND_ROOT

logger = logging.getLogger(__name__)

AUDIT_DIR = BACKEND_ROOT / "data" / "audit"
AUDIT_FILE = AUDIT_DIR / "safeguarding_events.jsonl"


def submit_safeguarding_flag(
    category: str,
    severity: str,
    user_summary: str,
    user_confirmed: bool = False,
) -> dict[str, Any]:
    """Append auditable test event locally. Rejects unless user_confirmed is True."""
    if not user_confirmed:
        return {
            "status": "rejected",
            "reason": "user_confirmed must be true. No flag was submitted.",
        }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "severity": severity,
        "user_summary": user_summary[:500],
        "user_confirmed": True,
        "environment": "poc_test_sink",
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    logger.info("Safeguarding flag recorded (test sink): category=%s severity=%s", category, severity)

    return {
        "status": "recorded",
        "message": (
            "Your concern has been logged in the PoC test system. "
            "In production this would route to your school's safeguarding lead. "
            "Please also speak directly with a trusted adult or school contact."
        ),
        "event_id": event["timestamp"],
    }
