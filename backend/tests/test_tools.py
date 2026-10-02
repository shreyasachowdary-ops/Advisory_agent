"""MCP tool unit tests."""

from mcp_server.tools.activity_plan import create_activity_plan
from mcp_server.tools.safeguarding import submit_safeguarding_flag
from mcp_server.tools.school_policy import get_school_policy


def test_create_activity_plan():
    plan = create_activity_plan(
        age_band="4_years",
        goal="turn_taking_during_play",
        days=5,
        setting="classroom",
    )
    assert plan["title"]
    assert len(plan["daily_plan"]) == 5
    assert plan["editable"] is True


def test_safeguarding_rejects_unconfirmed():
    result = submit_safeguarding_flag(
        category="test",
        severity="low",
        user_summary="test",
        user_confirmed=False,
    )
    assert result["status"] == "rejected"


def test_safeguarding_accepts_confirmed():
    result = submit_safeguarding_flag(
        category="test",
        severity="low",
        user_summary="test event",
        user_confirmed=True,
    )
    assert result["status"] == "recorded"


def test_get_school_policy():
    result = get_school_policy("bullying")
    assert result["policy_type"] == "bullying"
    assert "text" in result
