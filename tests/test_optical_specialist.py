"""Tests for optical specialist adapter (Ticket T05)."""
from datetime import UTC, datetime

import pytest

from satquery.contracts import AssetRecord, GridSpec, SingleParams
from satquery.specialists.optical import OpticalSpecialist


@pytest.fixture
def optical_asset():
    return AssetRecord(
        asset_id="ast_opt_001",
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


@pytest.fixture
def sar_asset():
    return AssetRecord(
        asset_id="ast_sar_001",
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


def test_optical_specialist_labelled_fixture_vqa(optical_asset):
    # FIX-02: scripted output is an explicitly labelled fixture, not a real result.
    specialist = OpticalSpecialist(scripted=True)
    params = SingleParams(task="vqa", question="Is there any water body present?")

    result = specialist.run(asset=optical_asset, params=params)

    assert len(result.outputs) == 1
    assert result.outputs[0].name == "finding"
    assert result.outputs[0].artifact.kind == "text"
    assert result.checks[0].status == "pass"


def test_optical_specialist_blocks_radar(sar_asset):
    specialist = OpticalSpecialist()
    params = SingleParams(task="vqa", question="Analyze structures")

    with pytest.raises(ValueError, match="MODALITY_MISMATCH"):
        specialist.run(asset=sar_asset, params=params)


def test_optical_specialist_contract_conforms_to_schema():
    contract = OpticalSpecialist.CONTRACT
    assert contract.tool_id == "optical_vqa"
    assert contract.task == "vqa"
    assert contract.output_kinds == ("text",)
    assert contract.inputs[0].kind == "asset"
    assert contract.inputs[0].modalities == ("optical",)
