"""Tests for durable job lifecycle store (Ticket T03)."""
import pytest
from satquery.storage.jobs import JobStore

@pytest.fixture
def store():
    return JobStore(":memory:")

def test_create_and_fetch_run(store):
    run = store.create_run(
        query="Analyze temporal change",
        assets={"before": "ast_1", "after": "ast_2"}
    )
    assert run["run_id"] == "run_0001"
    assert run["status"] == "queued"
    assert run["assets"]["before"] == "ast_1"

    fetched = store.get_run("run_0001")
    assert fetched == run

def test_idempotency_prevents_duplicate_runs(store):
    key = "client-req-abc-123"
    run1 = store.create_run("Query 1", {"img": "1"}, idempotency_key=key)
    run2 = store.create_run("Query 1 duplicate", {"img": "1"}, idempotency_key=key)
    
    assert run1["run_id"] == run2["run_id"]
    assert run1["query"] == run2["query"]

def test_state_transitions(store):
    run = store.create_run("Query", {"img": "1"})
    run_id = run["run_id"]

    store.update_status(run_id, "running")
    assert store.get_run(run_id)["status"] == "running"

    store.update_status(run_id, "succeeded")
    assert store.get_run(run_id)["status"] == "succeeded"

    # Terminal state cannot regress back to running or queued
    with pytest.raises(ValueError, match="Cannot transition from terminal state"):
        store.update_status(run_id, "running")

def test_invalid_state_rejected(store):
    run = store.create_run("Query", {"img": "1"})
    with pytest.raises(ValueError, match="Invalid state"):
        store.update_status(run["run_id"], "floating_in_space")
