"""HTTP transport schemas for SatQuery API."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from satquery.contracts import ClaimRecord

class RunSubmissionRequest(BaseModel):
    query: str = Field(..., min_length=3, description="User's natural language question")
    assets: Dict[str, str] = Field(..., min_length=1, description="Asset slot bindings (e.g. {'before': 'ast_1'})")
    idempotency_key: Optional[str] = Field(None, description="Client token to prevent duplicate runs")

class RunRevisionRequest(BaseModel):
    changed_assets: Dict[str, str] = Field(default_factory=dict, description="Replaced asset IDs")
    revised_aoi: Optional[Dict[str, float]] = Field(None, description="Updated bounding box/polygon")

class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    task: Optional[str] = None
    claims: List[ClaimRecord] = Field(default_factory=list)
    error: Optional[str] = None
