"""Tests for optical-SAR fusion specialist adapter (Ticket T08)."""
from datetime import datetime, timezone
import pytest

from satquery.contracts import AssetRecord, FusionParams, GridSpec
from satquery.specialists.fusion import FusionSpecialist


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
        acquired_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
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
        acquired_at=datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc),
        origin="public",
        processing_level="rtc",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


def test_fusion_specialist_successful_run(optical_asset, sar_asset):
    specialist = FusionSpecialist()
    params = FusionParams(
        task="cross_modal",
        target="urban_water",
        question="Cross-verify water extent under cloud shadow.",
    )

    result = specialist.run(optical=optical_asset, sar=sar_asset, params=params)

    assert len(result.outputs) == 2
    output_names = {o.name for o in result.outputs}
    assert output_names == {"fusion_summary", "fusion_metrics"}
    assert result.checks[0].check_id == "cross_modal_alignment_check"
    assert result.checks[0].status == "pass"


def test_fusion_specialist_rejects_swapped_modalities(optical_asset, sar_asset):
    specialist = FusionSpecialist()
    params = FusionParams(task="cross_modal", target="built_up")

    # Passing SAR into the optical slot must raise an error
    with pytest.raises(ValueError, match="MODALITY_MISMATCH"):
        specialist.run(optical=sar_asset, sar=optical_asset, params=params)


def test_fusion_specialist_rejects_optical_only(optical_asset):
    specialist = FusionSpecialist()
    params = FusionParams(task="cross_modal", target="built_up")

    # Both slots cannot be optical; radar is mandatory for fusion
    with pytest.raises(ValueError, match="MODALITY_MISMATCH"):
        specialist.run(optical=optical_asset, sar=optical_asset, params=params)
