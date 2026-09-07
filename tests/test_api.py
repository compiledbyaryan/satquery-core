"""Tests for HTTP transport contracts (Ticket T02)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from satquery.api.routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_submit_run_success():
    payload = {
        "query": "Did built-up area increase?",
        "assets": {"before": "ast_001", "after": "ast_002"}
    }
    res = client.post("/api/v1/runs", json=payload)
    assert res.status_code == 202
    data = res.json()
    assert "run_id" in data
    assert data["status"] == "queued"

def test_submit_run_invalid_payload():
    # Empty query must be rejected by Pydantic validation
    res = client.post("/api/v1/runs", json={"query": "", "assets": {}})
    assert res.status_code == 422

def test_get_nonexistent_run():
    res = client.get("/api/v1/runs/nonexistent_id")
    assert res.status_code == 404
