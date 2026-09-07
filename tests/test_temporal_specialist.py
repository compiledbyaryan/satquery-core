"""Tests for bi-temporal specialist adapter (Ticket T07)."""
from datetime import datetime, timezone
import pytest

from satquery.contracts import AssetRecord, GridSpec, TemporalParams
from satquery.specialists.temporal import TemporalSpecialist


@pytest.fixture
def before_asset():
    return AssetRecord(
        asset_id="ast_opt_2026_01",
        version_id="v1",
        sha256="1" * 64,
        format="geotiff",
        modality="optical",
        sensor="sentinel2",
        bands=("red", "green", "blue"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        origin="public",
        processing_level="l2a",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


@pytest.fixture
def after_asset():
    return AssetRecord(
        asset_id="ast_opt_2026_06",
        version_id="v1",
        sha256="2" * 64,
        format="geotiff",
        modality="optical",
        sensor="sentinel2",
        bands=("red", "green", "blue"),
        width=256,
        height=256,
        acquired_at=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
        origin="public",
        processing_level="l2a",
        grid=GridSpec(crs="EPSG:32643", affine=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)),
    )


def test_temporal_specialist_success(before_asset, after_asset):
    specialist = TemporalSpecialist()
    params = TemporalParams(task="change_description", target="built_up")

    result = specialist.run(before=before_asset, after=after_asset, params=params)

    assert len(result.outputs) == 2
    output_names = {o.name for o in result.outputs}
    assert output_names == {"change_summary", "change_mask"}
    assert result.checks[0].check_id == "temporal_order_check"
    assert result.checks[0].status == "pass"


def test_temporal_specialist_rejects_inverted_dates(before_asset, after_asset):
    specialist = TemporalSpecialist()
    params = TemporalParams(task="change_description", target="built_up")

    # Pass after as before, and before as after (reversed time)
    with pytest.raises(ValueError, match="TEMPORAL_ORDER"):
        specialist.run(before=after_asset, after=before_asset, params=params)


def test_temporal_specialist_rejects_identical_dates(before_asset):
    specialist = TemporalSpecialist()
    params = TemporalParams(task="change_description", target="built_up")

    # Identical acquisition dates cannot represent change
    with pytest.raises(ValueError, match="TEMPORAL_ORDER"):
        specialist.run(before=before_asset, after=before_asset, params=params)
