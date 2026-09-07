"""FastAPI routes wired to durable JobStore and Feedback router (Tickets T03 & T11)."""
from fastapi import APIRouter, Header, HTTPException, status

from satquery.api.feedback import feedback_router, shared_job_store
from satquery.api.schemas import RunRevisionRequest, RunStatusResponse, RunSubmissionRequest

router = APIRouter(prefix="/api/v1")
store = shared_job_store  # Unify storage instance

@router.post("/runs", response_model=RunStatusResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_run(
    req: RunSubmissionRequest,
    x_owner_id: str = Header(default="scientist_01", alias="X-Owner-ID"),
) -> RunStatusResponse:
    run = store.create_run(
        query=req.query,
        assets=req.assets,
        owner_id=x_owner_id,
        idempotency_key=req.idempotency_key,
    )
    return RunStatusResponse.model_validate(
        {
            "run_id": run["run_id"],
            "status": run["status"],
            "task": run["task"],
            "claims": [],
            "error": run["error"],
        }
    )

@router.get("/runs/{run_id}", response_model=RunStatusResponse)
def get_run_status(run_id: str) -> RunStatusResponse:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunStatusResponse.model_validate(
        {
            "run_id": run["run_id"],
            "status": run["status"],
            "task": run["task"],
            "claims": [],
            "error": run["error"],
        }
    )

@router.post("/runs/{run_id}/revise", response_model=RunStatusResponse)
def revise_run(run_id: str, req: RunRevisionRequest) -> RunStatusResponse:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    updated = store.update_status(run_id, "validating")
    return RunStatusResponse.model_validate(
        {
            "run_id": updated["run_id"],
            "status": updated["status"],
            "task": updated["task"],
            "claims": [],
            "error": updated["error"],
        }
    )

# Include feedback and export routes
router.include_router(feedback_router)
