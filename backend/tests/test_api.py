"""API endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "kb_version" in data


@pytest.mark.asyncio
async def test_chat_normal(client):
    resp = await client.post(
        "/api/chat",
        json={
            "message": "My 4-year-old is upset at preschool drop-off.",
            "audience": "parent",
            "age_band": "4_years",
            "language": "en",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "normal"
    assert len(data["answer"]) > 0


@pytest.mark.asyncio
async def test_chat_urgent_escalation(client):
    resp = await client.post(
        "/api/chat",
        json={
            "message": "A child told me they want to kill themselves.",
            "audience": "teacher",
            "age_band": "5_years",
            "language": "en",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["risk_level"] == "urgent"
    assert data["requires_human_review"] is True


@pytest.mark.asyncio
async def test_feedback(client):
    resp = await client.post("/api/feedback", json={"rating": "helpful"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_safeguarding_rejects_unconfirmed(client):
    resp = await client.post(
        "/api/safeguarding/confirm",
        json={
            "category": "abuse",
            "severity": "high",
            "user_summary": "test",
            "user_confirmed": False,
        },
    )
    assert resp.status_code == 400
