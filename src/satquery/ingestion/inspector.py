"""Secure raster ingestion and metadata extraction (Ticket T04)."""
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import rasterio
from rasterio.errors import RasterioIOError

from satquery.contracts import AssetRecord, GridSpec

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB upload limit
ALLOWED_DRIVERS = {"GTiff", "PNG", "JPEG"}

class IngestionError(Exception):
    pass

def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def inspect_raster(
    file_path: Path,
    asset_id: str,
    modality: str,
    sensor: str,
    acquired_at: datetime | None = None,
    origin: Literal["public", "synthetic", "restricted"] = "restricted",
) -> AssetRecord:
    if not file_path.exists():
        raise IngestionError(f"File not found: {file_path}")

    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise IngestionError(f"File exceeds maximum size limit of {MAX_FILE_SIZE_BYTES} bytes")

    sha256_hash = compute_sha256(file_path)

    try:
        with rasterio.open(file_path) as src:
            if src.driver not in ALLOWED_DRIVERS:
                raise IngestionError(f"Driver '{src.driver}' not permitted. Allowed: {ALLOWED_DRIVERS}")

            width = src.width
            height = src.height
            band_count = src.count

            crs_str = src.crs.to_string() if src.crs else None

            # Affine tuple: (a, b, c, d, e, f)
            t = src.transform
            affine_tuple = (t.a, t.b, t.c, t.d, t.e, t.f)

            grid = None
            if crs_str:
                grid = GridSpec(crs=crs_str, affine=affine_tuple)

            format_type = "geotiff" if src.driver == "GTiff" else src.driver.lower()
            band_names = tuple(f"band_{i+1}" for i in range(band_count))
            acquisition = acquired_at or datetime.now(UTC)

            return AssetRecord(
                asset_id=asset_id,
                version_id="v1",
                sha256=sha256_hash,
                format=format_type,
                modality=modality,
                sensor=sensor,
                bands=band_names,
                width=width,
                height=height,
                acquired_at=acquisition,
                origin=origin,
                processing_level="raw",
                grid=grid,
            )
    except RasterioIOError as e:
        raise IngestionError(f"Failed to decode raster file: {e}") from e
