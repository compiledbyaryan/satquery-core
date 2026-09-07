"""Tests for plan controller, registry, and atomic evidence (Ticket T10)."""
from datetime import datetime, timezone
import pytest

from satquery.contracts import (
    ArtifactRef,
    AssetInput,
    AssetRecord,
    CheckResult,
    ClaimRecord,
    GridSpec,
    InputSlot,
    PlanRecord,
    PlanStep,
    SingleParams,
    ToolContract,
)
from satquery.controller.executor import execute_plan
from satquery.controller.registry import ToolRegistry
from satquery.evidence.store import ArtifactStore
from satquery.specialists.optical import OpticalSpecialist


@pytest.fixture
def optical_asset():
    return AssetRecord(
        asset_id="ast_opt_ctrl_01",
        version_id="v1",
        sha256="a" * 64,
        format="geotiff",
        modality="optical",
        sensor="sentinel2",
        bands=("red", "green", "blue"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        origin="public",
        processing_level="l2a",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


@pytest.fixture
def valid_plan():
    step = PlanStep(
        step_id="step_01",
        tool_id="optical_vqa",
        tool_version="0.1.0",
        inputs=(AssetInput(slot="asset", asset_version_id="ast_opt_ctrl_01"),),
        params=SingleParams(task="vqa", question="Identify water extent."),
    )
    return PlanRecord(
        plan_id="plan_ctrl_001",
        task="vqa",
        asset_versions=("ast_opt_ctrl_01",),
        steps=(step,),
    )


def test_execute_plan_success(optical_asset, valid_plan):
    store = ArtifactStore()
    store.register_asset(optical_asset)

    registry = ToolRegistry()
    specialist = OpticalSpecialist()
    registry.register(specialist.CONTRACT, specialist)

    outcome = execute_plan(plan=valid_plan, registry=registry, store=store, mode="real")

    assert outcome.status == "succeeded"
    assert len(outcome.events) == 1
    assert outcome.events[0].status == "succeeded"
    assert len(outcome.artifacts) == 1
    assert store.has_artifact(outcome.artifacts[0].artifact_id)


def test_execute_plan_rejects_unknown_tool(optical_asset, valid_plan):
    store = ArtifactStore()
    store.register_asset(optical_asset)
    registry = ToolRegistry()  # Empty registry

    outcome = execute_plan(plan=valid_plan, registry=registry, store=store, mode="real")

    assert outcome.status == "failed"
    assert outcome.error.code == "UNSUPPORTED"
    assert "UNREGISTERED_TOOL" in outcome.error.message


def test_execute_plan_blocks_mock_in_real_mode(optical_asset, valid_plan):
    store = ArtifactStore()
    store.register_asset(optical_asset)
    registry = ToolRegistry()

    # Create mock contract
    mock_contract = ToolContract(
        tool_id="optical_vqa",
        version="0.1.0",
        task="vqa",
        inputs=(InputSlot(name="image", modalities=("optical",), required_bands=("red", "green", "blue")),),
        output_kinds=("text",),
        params_kind="single",
        implementation="mock",
        timeout_seconds=30,
        max_memory_mb=512,
    )
    registry.register(mock_contract, OpticalSpecialist())

    outcome = execute_plan(plan=valid_plan, registry=registry, store=store, mode="real")

    assert outcome.status == "failed"
    assert outcome.error.code == "UNSUPPORTED"
    assert "MOCK_PROHIBITED" in outcome.error.message


def test_execute_plan_timeout_never_yields_success(optical_asset, valid_plan):
    store = ArtifactStore()
    store.register_asset(optical_asset)
    registry = ToolRegistry()
    specialist = OpticalSpecialist()
    registry.register(specialist.CONTRACT, specialist)

    outcome = execute_plan(
        plan=valid_plan,
        registry=registry,
        store=store,
        mode="real",
        simulate_timeout=True,
    )

    assert outcome.status == "failed"
    assert outcome.error.code == "TIMEOUT"


def test_atomic_claim_requires_store_evidence():
    store = ArtifactStore()
    real_artifact = ArtifactRef(artifact_id="art_real", sha256="c" * 64, kind="text")
    store.store_artifact(real_artifact)

    check = CheckResult(check_id="chk_01", status="pass", required=True, detail="Confirmed")

    # Valid claim referencing stored artifact
    claim_valid = ClaimRecord(
        claim_id="clm_01",
        run_id="run_01",
        text="Valid observation text",
        kind="observation",
        status="supported",
        evidence=(real_artifact,),
        checks=(check,),
    )
    store.record_claim(claim_valid)

    # Invalid claim referencing unowned / missing artifact
    phantom_artifact = ArtifactRef(artifact_id="art_ghost", sha256="d" * 64, kind="text")
    claim_invalid = ClaimRecord(
        claim_id="clm_02",
        run_id="run_01",
        text="Phantom observation text",
        kind="observation",
        status="supported",
        evidence=(phantom_artifact,),
        checks=(check,),
    )
    with pytest.raises(ValueError, match="CLAIM_UNSUPPORTED_BY_STORE"):
        store.record_claim(claim_invalid)
