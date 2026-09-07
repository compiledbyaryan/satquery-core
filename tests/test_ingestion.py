"""Tests for raster ingestion and inspection (Ticket T04)."""
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from satquery.ingestion.inspector import inspect_raster, IngestionError

@pytest.fixture
def sample_geotiff(tmp_path):
    file_path = tmp_path / "test_optical.tif"
    data = np.ones((3, 64, 64), dtype=np.uint8) * 128
    transform = from_origin(500000.0, 3000000.0, 10.0, 10.0)

    with rasterio.open(
        file_path,
        "w",
        driver="GTiff",
        height=64,
        width=64,
        count=3,
        dtype=data.dtype,
        crs="EPSG:32643",
        transform=transform,
    ) as dst:
        dst.write(data)

    return file_path

def test_inspect_valid_geotiff(sample_geotiff):
    record = inspect_raster(
        file_path=sample_geotiff,
        asset_id="ast_test_01",
        modality="optical",
        sensor="sentinel2",
        acquired_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        origin="restricted"
    )

    assert record.asset_id == "ast_test_01"
    assert record.width == 64
    assert record.height == 64
    assert len(record.bands) == 3
    assert record.origin == "restricted"
    assert record.grid is not None
    assert record.grid.crs == "EPSG:32643"
    assert len(record.sha256) == 64

def test_inspect_missing_file():
    with pytest.raises(IngestionError, match="File not found"):
        inspect_raster(
            file_path=Path("/tmp/nonexistent.tif"),
            asset_id="ast_err",
            modality="optical",
            sensor="sentinel2"
        )
