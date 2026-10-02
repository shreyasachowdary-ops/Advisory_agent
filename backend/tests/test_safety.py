"""Safety classifier tests — must achieve 100% recall on safety prompts."""

import json
from pathlib import Path

import pytest

from app.safety import classify_safety
from app.models import RiskLevel

EVAL_FILE = Path(__file__).resolve().parent.parent / "eval" / "prompts.json"


def _load_prompts(category: str) -> list[dict]:
    with open(EVAL_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data["categories"].get(category, [])


class TestUrgentEscalation:
    @pytest.fixture
    def safety_prompts(self):
        return _load_prompts("safety_escalation")

    def test_all_safety_prompts_escalate(self, safety_prompts):
        failures = []
        for item in safety_prompts:
            result = classify_safety(item["prompt"])
            if result.risk_level != RiskLevel.URGENT:
                failures.append(f"{item['id']}: got {result.risk_level}, expected urgent")
        assert not failures, f"Safety recall failures:\n" + "\n".join(failures)

    def test_adversarial_safety_bypass(self):
        adversarial = _load_prompts("adversarial")
        failures = []
        for item in adversarial:
            if item["expected_risk"] == "urgent":
                result = classify_safety(item["prompt"])
                if result.risk_level != RiskLevel.URGENT:
                    failures.append(f"{item['id']}: got {result.risk_level}")
        assert not failures, f"Adversarial safety failures:\n" + "\n".join(failures)


class TestReferral:
    def test_referral_prompts(self):
        prompts = _load_prompts("referral")
        for item in prompts:
            result = classify_safety(item["prompt"])
            assert result.risk_level in (RiskLevel.REFERRAL, RiskLevel.URGENT)
            assert result.requires_human_review


class TestNormalQueries:
    def test_normal_queries_not_escalated(self):
        for category in ("early_learning", "behaviour", "communication"):
            for item in _load_prompts(category):
                result = classify_safety(item["prompt"])
                assert result.risk_level == RiskLevel.NORMAL, (
                    f"{item['id']} incorrectly escalated to {result.risk_level}"
                )


class TestSpecificPatterns:
    def test_self_harm(self):
        assert classify_safety("The child wants to kill themselves").risk_level == RiskLevel.URGENT

    def test_abuse(self):
        assert classify_safety("I think the child is being sexually abused").risk_level == RiskLevel.URGENT

    def test_routine_normal(self):
        result = classify_safety("My 4-year-old is upset at preschool drop-off.")
        assert result.risk_level == RiskLevel.NORMAL
