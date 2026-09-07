"""Tests for SAR specialist adapter (Ticket T06)."""
from datetime import UTC, datetime

import pytest

from satquery.contracts import AssetRecord, GridSpec, SingleParams
from satquery.specialists.sar import SARSpecialist


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


def test_sar_specialist_successful_vqa(sar_asset):
    specialist = SARSpecialist()
    params = SingleParams(task="vqa", question="Is there flood water present?")

    result = specialist.run(asset=sar_asset, params=params)

    assert len(result.outputs) == 1
    assert result.outputs[0].name == "finding"
    assert result.outputs[0].artifact.kind == "text"
    assert "Low specular backscatter" in result.checks[0].detail or result.checks[0].status == "pass"


def test_sar_specialist_blocks_optical(optical_asset):
    specialist = SARSpecialist()
    params = SingleParams(task="vqa", question="Check backscatter")

    with pytest.raises(ValueError, match="MODALITY_MISMATCH"):
        specialist.run(asset=optical_asset, params=params)


def test_sar_specialist_contract_conforms():
    contract = SARSpecialist.CONTRACT
    assert contract.tool_id == "sar_vqa"
    assert contract.task == "vqa"
    assert contract.inputs[0].modalities == ("sar",)
    assert contract.inputs[0].required_bands == ("vv", "vh")
