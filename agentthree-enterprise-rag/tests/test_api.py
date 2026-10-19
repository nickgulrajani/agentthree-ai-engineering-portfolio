"""API smoke tests — local only, no external network."""

from __future__ import annotations

from fastapi.testclient import TestClient

from agentthree_enterprise_rag.api import app


client = TestClient(app)


def test_health_zero_cost() -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["zeroCost"] is True
    assert body["billableSurface"] is False
    assert body["chunkCount"] > 0


def test_principals() -> None:
    r = client.get("/api/principals")
    assert r.status_code == 200
    ids = {p["principalId"] for p in r.json()["principals"]}
    assert {"alice_hr", "bob_eng", "eve_contractor"} <= ids


def test_ask_alice_answers() -> None:
    r = client.post(
        "/api/ask",
        json={
            "principal_id": "alice_hr",
            "question": "What is the monthly home-office stipend for fully remote employees?",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["answered"] is True
    assert any(c["docId"] == "POL-HR-001" for c in body["citations"])
    assert "$75" in body["answer"]


def test_ask_bob_refuses() -> None:
    r = client.post(
        "/api/ask",
        json={
            "principal_id": "bob_eng",
            "question": "What is the monthly home-office stipend for fully remote employees?",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["answered"] is False
    assert body["citations"] == []


def test_evaluation_perfect() -> None:
    r = client.get("/api/evaluation")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["score"] == 1.0
