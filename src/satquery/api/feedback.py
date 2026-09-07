"""Scientist feedback and authenticated export endpoints (Ticket T11)."""
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from satquery.reports.builder import build_report
from satquery.storage.jobs import JobStore

# Route prefix is inherited from parent router in routes.py
feedback_router = APIRouter()
shared_job_store = JobStore()


class FeedbackCreate(BaseModel):
    claim_id: str | None = None
    version: str = "1.0"
    rating: int | None = Field(None, ge=1, le=5)
    notes: str = Field(..., min_length=1, max_length=2000)
    is_private: bool = True  # Sensitive feedback is private by default


class FeedbackResponse(BaseModel):
    feedback_id: str
    run_id: str
    claim_id: str | None
    version: str
    owner_id: str
    rating: int | None
    notes: str
    is_private: bool
    created_at: str


@feedback_router.post(
    "/runs/{run_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(
    run_id: str,
    body: FeedbackCreate,
    x_owner_id: str = Header(..., alias="X-Owner-ID"),
):
    run = shared_job_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    record = shared_job_store.record_feedback(
        run_id=run_id,
        owner_id=x_owner_id,
        notes=body.notes,
        claim_id=body.claim_id,
        version=body.version,
        rating=body.rating,
        is_private=body.is_private,
    )
    return record


@feedback_router.get(
    "/runs/{run_id}/feedback",
    response_model=list[FeedbackResponse],
)
def list_feedback(
    run_id: str,
    x_owner_id: str = Header(..., alias="X-Owner-ID"),
):
    run = shared_job_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return shared_job_store.get_feedback_for_run(run_id, caller_id=x_owner_id)


@feedback_router.get(
    "/runs/{run_id}/report",
)
def download_report(
    run_id: str,
    x_owner_id: str = Header(..., alias="X-Owner-ID"),
):
    try:
        artifact = build_report(run_id=run_id, owner_id=x_owner_id, job_store=shared_job_store)
        return {
            "artifact_id": artifact.artifact_id,
            "sha256": artifact.sha256,
            "kind": artifact.kind,
            "status": "ready",
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")
    except PermissionError as pe:
        # Multi-tenant isolation: fail closed with no data leakage
        raise HTTPException(status_code=403, detail=str(pe))
