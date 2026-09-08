"""FIX-02: scripted specialists must not execute as real implementations.

Boundary: the four scripted adapters are explicitly labelled fixtures
(CONTRACT.implementation == "mock"). Their default run() refuses with
MODEL_UNAVAILABLE without a real provider; an explicit scripted=True
opt-in preserves the labelled UI-fixture path. Real-mode execution through
the controller fails honestly instead of returning rehearsed answers.
"""
from datetime import UTC, datetime

import pytest

from satquery.contracts import (
    AssetInput,
    AssetRecord,
    FusionParams,
    GridSpec,
    InputSlot,
    PlanRecord,
    PlanStep,
    SingleParams,
    TemporalParams,
    ToolContract,
)
from satquery.controller.executor import execute_plan
from satquery.controller.registry import ToolRegistry
from satquery.evidence.store import ArtifactStore
from satquery.specialists.fusion import FusionSpecialist
from satquery.specialists.optical import OpticalSpecialist
from satquery.specialists.sar import SARSpecialist
from satquery.specialists.temporal import TemporalSpecialist


def _optical_asset() -> AssetRecord:
    return AssetRecord(
        asset_id="ast_fix02_opt",
        version_id="v1",
        sha256="a" * 64,
        format="geotiff",
        modality="optical",
        sensor="sentinel2",
        bands=("red", "green", "blue"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        origin="public",
        processing_level="l2a",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


def _sar_asset() -> AssetRecord:
    return AssetRecord(
        asset_id="ast_fix02_sar",
        version_id="v1",
        sha256="b" * 64,
        format="geotiff",
        modality="sar",
        sensor="sentinel1",
        bands=("vv", "vh"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        origin="public",
        processing_level="rtc",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


def test_scripted_contracts_are_labelled_mock():
    assert OpticalSpecialist.CONTRACT.implementation == "mock"
    assert SARSpecialist.CONTRACT.implementation == "mock"
    assert TemporalSpecialist.CONTRACT.implementation == "mock"
    assert FusionSpecialist.CONTRACT.implementation == "mock"


def test_default_optical_run_is_unavailable_without_provider():
    specialist = OpticalSpecialist()
    params = SingleParams(task="vqa", question="Is there any water body present?")
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        specialist.run(asset=_optical_asset(), params=params)


def test_default_sar_run_is_unavailable_without_provider():
    specialist = SARSpecialist()
    params = SingleParams(task="vqa", question="Is there flood water present?")
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        specialist.run(asset=_sar_asset(), params=params)


def test_default_temporal_run_is_unavailable_without_provider():
    before = _optical_asset()
    after = AssetRecord(
        asset_id="ast_fix02_after",
        version_id="v1",
        sha256="c" * 64,
        format="geotiff",
        modality="optical",
        sensor="sentinel2",
        bands=("red", "green", "blue"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 6, 20, 10, 0, tzinfo=UTC),
        origin="public",
        processing_level="l2a",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )
    specialist = TemporalSpecialist()
    params = TemporalParams(task="change_description", target="built_up")
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        specialist.run(before=before, after=after, params=params)


def test_default_fusion_run_is_unavailable_without_provider():
    specialist = FusionSpecialist()
    params = FusionParams(task="cross_modal", target="built_up")
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        specialist.run(optical=_optical_asset(), sar=_sar_asset(), params=params)


def test_nonexistent_model_path_still_unavailable():
    specialist = OpticalSpecialist(model_path="/nonexistent/checkpoint.bin")
    params = SingleParams(task="vqa", question="Is there any water body present?")
    with pytest.raises(ValueError, match="MODEL_UNAVAILABLE"):
        specialist.run(asset=_optical_asset(), params=params)


def test_explicit_scripted_opt_in_preserves_labelled_fixture():
    specialist = OpticalSpecialist(scripted=True)
    params = SingleParams(task="vqa", question="Is there any water body present?")
    result = specialist.run(asset=_optical_asset(), params=params)
    assert len(result.outputs) == 1
    assert result.outputs[0].name == "finding"


def test_real_mode_execution_refuses_scripted_tool():
    asset = _optical_asset()
    store = ArtifactStore()
    store.register_asset(asset)
    registry = ToolRegistry()
    registry.register(OpticalSpecialist.CONTRACT, OpticalSpecialist())

    step = PlanStep(
        step_id="step_01",
        tool_id="optical_vqa",
        tool_version="0.1.0",
        inputs=(AssetInput(slot="asset", asset_version_id="ast_fix02_opt"),),
        params=SingleParams(task="vqa", question="Identify water extent."),
    )
    plan = PlanRecord(
        plan_id="plan_fix02_001",
        task="vqa",
        asset_versions=("ast_fix02_opt",),
        steps=(step,),
    )
    outcome = execute_plan(plan=plan, registry=registry, store=store, mode="real")
    assert outcome.status == "failed"
    assert outcome.error is not None
    assert "MOCK_PROHIBITED" in outcome.error.message


def test_mock_mode_execution_allows_labelled_fixture():
    asset = _optical_asset()
    store = ArtifactStore()
    store.register_asset(asset)
    registry = ToolRegistry()
    registry.register(OpticalSpecialist.CONTRACT, OpticalSpecialist(scripted=True))

    step = PlanStep(
        step_id="step_01",
        tool_id="optical_vqa",
        tool_version="0.1.0",
        inputs=(AssetInput(slot="asset", asset_version_id="ast_fix02_opt"),),
        params=SingleParams(task="vqa", question="Identify water extent."),
    )
    plan = PlanRecord(
        plan_id="plan_fix02_002",
        task="vqa",
        asset_versions=("ast_fix02_opt",),
        steps=(step,),
    )
    outcome = execute_plan(plan=plan, registry=registry, store=store, mode="mock")
    assert outcome.status == "succeeded"
    assert len(outcome.artifacts) == 1


class _UnavailableRunner:
    def run(self, **kwargs: object) -> object:
        raise ValueError("MODEL_UNAVAILABLE: no real provider configured for probe tool")


def test_executor_reports_model_unavailable_honestly():
    contract = ToolContract(
        tool_id="probe_tool",
        version="0.1.0",
        task="vqa",
        inputs=(InputSlot(name="image", modalities=("optical",)),),
        output_kinds=("text",),
        params_kind="single",
        implementation="real",
        timeout_seconds=30,
        max_memory_mb=512,
    )
    asset = _optical_asset()
    store = ArtifactStore()
    store.register_asset(asset)
    registry = ToolRegistry()
    registry.register(contract, _UnavailableRunner())

    step = PlanStep(
        step_id="step_01",
        tool_id="probe_tool",
        tool_version="0.1.0",
        inputs=(AssetInput(slot="image", asset_version_id="ast_fix02_opt"),),
        params=SingleParams(task="vqa", question="Probe question."),
    )
    plan = PlanRecord(
        plan_id="plan_fix02_003",
        task="vqa",
        asset_versions=("ast_fix02_opt",),
        steps=(step,),
    )
    outcome = execute_plan(plan=plan, registry=registry, store=store, mode="real")
    assert outcome.status == "failed"
    assert outcome.error is not None
    assert outcome.error.code == "MODEL_UNAVAILABLE"
