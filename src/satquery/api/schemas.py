"""HTTP transport schemas for SatQuery API."""

from pydantic import BaseModel, Field

from satquery.contracts import ClaimRecord


class RunSubmissionRequest(BaseModel):
    query: str = Field(..., min_length=3, description="User's natural language question")
    assets: dict[str, str] = Field(..., min_length=1, description="Asset slot bindings (e.g. {'before': 'ast_1'})")
    idempotency_key: str | None = Field(None, description="Client token to prevent duplicate runs")

class RunRevisionRequest(BaseModel):
    changed_assets: dict[str, str] = Field(default_factory=dict, description="Replaced asset IDs")
    revised_aoi: dict[str, float] | None = Field(None, description="Updated bounding box/polygon")

class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    task: str | None = None
    claims: list[ClaimRecord] = Field(default_factory=list)
    error: str | None = None
