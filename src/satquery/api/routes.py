"""FastAPI routes wired to durable JobStore."""
from fastapi import APIRouter, HTTPException, status
from satquery.api.schemas import RunSubmissionRequest, RunRevisionRequest, RunStatusResponse
from satquery.storage.jobs import JobStore

router = APIRouter(prefix="/api/v1")
store = JobStore()  # In production this points to a persistent file path

@router.post("/runs", response_model=RunStatusResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_run(req: RunSubmissionRequest):
    run = store.create_run(
        query=req.query,
        assets=req.assets,
        idempotency_key=req.idempotency_key
    )
    return {
        "run_id": run["run_id"],
        "status": run["status"],
        "task": run["task"],
        "claims": [],
        "error": run["error"]
    }

@router.get("/runs/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": run["run_id"],
        "status": run["status"],
        "task": run["task"],
        "claims": [],
        "error": run["error"]
    }

@router.post("/runs/{run_id}/revise", response_model=RunStatusResponse)
def revise_run(run_id: str, req: RunRevisionRequest):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    updated = store.update_status(run_id, "validating")
    return {
        "run_id": updated["run_id"],
        "status": updated["status"],
        "task": updated["task"],
        "claims": [],
        "error": updated["error"]
    }
