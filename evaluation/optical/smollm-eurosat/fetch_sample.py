"""Fetch a fixed 12-image EuroSAT RGB sample with opaque filenames.

Source: timm/eurosat-rgb train split (HuggingFace mirror of EuroSAT,
Helber et al. 2019, Sentinel-2). Rows are selected by fixed index stride,
never by class label. Class labels and source image_ids are recorded ONLY in
manifest.json for audit; inference inputs are opaque sample_NN.png files.
A locally generated blank diagnostic image is stored as blank.png.

Writes: inputs/sample_01..12.png, inputs/blank.png, manifest.json
"""
import hashlib
import json
from pathlib import Path

from datasets import load_dataset
from PIL import Image

DATASET_ID = "timm/eurosat-rgb"
DATASET_REVISION = "b4e28552cd5f3932b6abc37eb20d3e84901ad728"
SPLIT = "train"
N_SAMPLES = 12
STRIDE = 1350  # 16200 train rows / 12 -> indices 0, 1350, ..., 14850

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    INPUTS.mkdir(parents=True, exist_ok=True)
    wanted = {i * STRIDE for i in range(N_SAMPLES)}
    ds = load_dataset(
        DATASET_ID,
        revision=DATASET_REVISION,
        split=SPLIT,
        streaming=True,
    )
    records = []
    slot = 0
    for row_index, ex in enumerate(ds):
        if row_index in wanted:
            slot += 1
            out = INPUTS / f"sample_{slot:02d}.png"
            img = ex["image"].convert("RGB")
            img.save(out)
            records.append(
                {
                    "opaque_file": out.name,
                    "dataset_row_index": row_index,
                    "source_image_id": ex["image_id"],
                    "source_label_id": int(ex["label"]),
                    "sha256": sha256_file(out),
                    "size_px": list(img.size),
                    "mode": img.mode,
                }
            )
            if slot == N_SAMPLES:
                break
    assert slot == N_SAMPLES, f"collected {slot} rows, expected {N_SAMPLES}"

    blank = Image.new("RGB", (64, 64), (128, 128, 128))
    blank_path = INPUTS / "blank.png"
    blank.save(blank_path)

    manifest = {
        "dataset": DATASET_ID,
        "dataset_revision": DATASET_REVISION,
        "split": SPLIT,
        "selection": f"fixed stride {STRIDE} over streaming {SPLIT} order, no label filtering",
        "n_samples": N_SAMPLES,
        "licence": (
            "MIT per the timm/eurosat-rgb dataset card. Underlying EuroSAT: Helber et "
            "al. 2019 (Sentinel-2). Used here as an unevaluated feasibility sample only."
        ),
        "acquisition_geospatial": "unknown (not provided by mirror; stays unknown)",
        "samples": records,
        "diagnostic": {
            "opaque_file": "blank.png",
            "sha256": sha256_file(blank_path),
            "description": "locally generated solid-gray 64x64 RGB diagnostic; not satellite data",
        },
    }
    with open(HERE / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {N_SAMPLES} samples + blank diagnostic; manifest at {HERE / 'manifest.json'}")


if __name__ == "__main__":
    main()
