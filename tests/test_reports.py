"""Acceptance and multi-tenant security tests for reports and feedback (Ticket T11)."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from satquery.api.feedback import shared_job_store
from satquery.api.routes import router
from satquery.contracts import ArtifactRef, CheckResult, ClaimRecord
from satquery.evidence.store import ArtifactStore
from satquery.reports.builder import build_report


@pytest.fixture
def clean_job_store():
    store = shared_job_store
    run = store.create_run(
        query="Assess mangrove canopy loss",
        assets={"before": "ast_opt_01", "after": "ast_opt_02"},
        owner_id="scientist_alpha",
    )
    store.save_outcome(
        run["run_id"],
        {
            "events": [
                {
                    "step_id": "step_01",
                    "tool_id": "temporal_change",
                    "tool_version": "0.1.0",
                    "status": "succeeded",
                    "outputs": ["art_change_mask_01"],
                }
            ]
        },
    )
    return store, run["run_id"]


def test_build_report_success_resolves_all_figures_and_claims(clean_job_store):
    store, run_id = clean_job_store
    artifact_store = ArtifactStore()

    real_art = ArtifactRef(artifact_id="art_change_mask_01", sha256="e" * 64, kind="mask")
    artifact_store.store_artifact(real_art)

    claim = ClaimRecord(
        claim_id="clm_mangrove_01",
        run_id=run_id,
        text="Canopy loss detected across 12.4 hectares",
        kind="measurement",
        status="supported",
        evidence=(real_art,),
        checks=(CheckResult(check_id="chk_01", status="pass", required=True, detail="Canopy loss confirmed within expected bounds"),),
    )

    report_ref = build_report(
        run_id=run_id,
        owner_id="scientist_alpha",
        job_store=store,
        artifact_store=artifact_store,
        claims=[claim],
    )

    assert report_ref.kind == "report"
    assert report_ref.artifact_id == f"rep_{run_id}"
    assert artifact_store.has_artifact(report_ref.artifact_id)


def test_build_report_multi_tenant_fails_closed(clean_job_store):
    store, run_id = clean_job_store
    artifact_store = ArtifactStore()

    # Unauthorized owner must be rejected with zero data leakage
    with pytest.raises(PermissionError, match="ACCESS_DENIED"):
        build_report(
            run_id=run_id,
            owner_id="unauthorized_attacker",
            job_store=store,
            artifact_store=artifact_store,
        )


def test_feedback_lifecycle_and_privacy():
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # 1. Submit a run under scientist_alpha
    sub_resp = client.post(
        "/api/v1/runs",
        json={"query": "Measure glacier retreat", "assets": {"sat": "ast_01"}},
        headers={"X-Owner-ID": "scientist_alpha"},
    )
    assert sub_resp.status_code == 202
    run_id = sub_resp.json()["run_id"]

    # 2. Record feedback (private by default)
    fb_resp = client.post(
        f"/api/v1/runs/{run_id}/feedback",
        json={
            "claim_id": "clm_glacier_01",
            "version": "1.0",
            "rating": 5,
            "notes": "Verified against ground GPS measurements.",
            "is_private": True,
        },
        headers={"X-Owner-ID": "scientist_alpha"},
    )
    assert fb_resp.status_code == 201
    assert fb_resp.json()["is_private"] is True

    # 3. Alpha can see their own private feedback
    list_alpha = client.get(f"/api/v1/runs/{run_id}/feedback", headers={"X-Owner-ID": "scientist_alpha"})
    assert len(list_alpha.json()) == 1

    # 4. Another scientist cannot see private feedback
    list_beta = client.get(f"/api/v1/runs/{run_id}/feedback", headers={"X-Owner-ID": "scientist_beta"})
    assert len(list_beta.json()) == 0


def test_download_report_endpoint_enforces_owner_authorization(clean_job_store):
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    _, run_id = clean_job_store

    # Authorized download
    ok_resp = client.get(f"/api/v1/runs/{run_id}/report", headers={"X-Owner-ID": "scientist_alpha"})
    assert ok_resp.status_code == 200
    assert ok_resp.json()["artifact_id"] == f"rep_{run_id}"

    # Unauthorized download returns 403 Forbidden
    denied_resp = client.get(f"/api/v1/runs/{run_id}/report", headers={"X-Owner-ID": "stranger_02"})
    assert denied_resp.status_code == 403
