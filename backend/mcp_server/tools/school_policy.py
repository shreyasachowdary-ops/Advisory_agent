"""Load mock school policy data."""

import json
from pathlib import Path
from typing import Any

from app.config import BACKEND_ROOT, settings

POLICIES_DIR = BACKEND_ROOT / "data" / "policies"


def get_school_policy(policy_type: str, school_id: str | None = None) -> dict[str, Any]:
    """Return approved policy text and contacts from mock JSON."""
    sid = school_id or settings.school_id
    policy_file = POLICIES_DIR / f"{sid}.json"

    if not policy_file.exists():
        return {
            "school_id": sid,
            "error": "Policy file not found",
            "available_types": [],
        }

    with open(policy_file, encoding="utf-8") as f:
        data = json.load(f)

    policies = data.get("policies", {})
    if policy_type not in policies:
        return {
            "school_id": sid,
            "error": f"Policy type '{policy_type}' not found",
            "available_types": list(policies.keys()),
        }

    policy = policies[policy_type]
    return {
        "school_id": sid,
        "school_name": data.get("school_name", sid),
        "policy_type": policy_type,
        "title": policy.get("title", policy_type),
        "text": policy.get("text", ""),
        "contacts": data.get("contacts", {}),
        "last_reviewed": policy.get("last_reviewed", ""),
    }
