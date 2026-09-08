"""CPU rescue for the pinned SmolVLM feasibility probe.

Rescue constraints (no downloads, no package changes):
- CUDA hidden before torch import; explicit CPU placement, float32.
- Eager attention; local_files_only on the existing pinned snapshot.
- eval mode + inference_mode; batch size one; short generation.
- Token tensors stay integer; no blanket dtype casts.

Writes a NEW run directory; never touches run_20260908* failure records.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import time
import traceback

os.environ["CUDA_VISIBLE_DEVICES"] = ""

from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

import psutil  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from transformers import AutoModelForMultimodalLM, AutoProcessor  # noqa: E402

MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"
MODEL_REVISION = "a7da5b986cb59b408707209984f360a5f4ad7e47"
DEFAULT_SNAPSHOT = Path(
    "/home/aryan/.cache/huggingface/hub/"
    "models--HuggingFaceTB--SmolVLM-500M-Instruct/snapshots/"
    f"{MODEL_REVISION}"
)
CAPTION_PROMPT = (
    "Describe the visible scene in one concise sentence. Mention only features visible "
    "in the image; do not infer location, date, sensor, or physical measurements."
)
QUESTION_PROMPT = (
    "Does this image appear to contain a large body of water? Answer yes, no, or "
    "uncertain, then give one short visual reason."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model-snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=24)
    parser.add_argument("--image", default="sample_01.png")
    parser.add_argument("--second-image", default="blank.png")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def tensor_summary(inputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summary = {}
    for name, value in inputs.items():
        if isinstance(value, torch.Tensor):
            summary[name] = {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "device": str(value.device),
            }
    return summary


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_image(inputs_dir: Path, manifest: dict[str, Any], opaque_file: str) -> tuple[Path, str]:
    if opaque_file == manifest["diagnostic"]["opaque_file"]:
        expected = manifest["diagnostic"]["sha256"]
        kind = "blank_diagnostic"
    else:
        matches = [s for s in manifest["samples"] if s["opaque_file"] == opaque_file]
        if not matches:
            raise ValueError(f"Image not in manifest: {opaque_file}")
        expected = matches[0]["sha256"]
        kind = "benchmark"
    image_path = inputs_dir / opaque_file
    actual = sha256_file(image_path)
    if actual != expected:
        raise ValueError(f"Hash mismatch for {opaque_file}")
    return image_path, kind


def main() -> int:
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == ""
    assert not torch.cuda.is_available(), "CUDA must be hidden for the CPU rescue"
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    results_path = args.output_dir / "invocations.jsonl"
    summary_path = args.output_dir / "run_summary.json"
    started_at = datetime.now(UTC)
    process = psutil.Process()
    summary: dict[str, Any] = {
        "status": "loading",
        "mode": "cpu_rescue",
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "torch_cuda_available": torch.cuda.is_available(),
        "torch_threads": torch.get_num_threads(),
        "started_at": started_at.isoformat(),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "model_snapshot": str(args.model_snapshot.resolve()),
        "manifest": str(args.manifest.resolve()),
        "max_new_tokens": args.max_new_tokens,
        "generation": {"do_sample": False},
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("torch", "torchvision", "transformers", "Pillow", "psutil", "huggingface-hub")
        },
        "cpu_rss_before_load_bytes": process.memory_info().rss,
    }
    write_json(summary_path, summary)

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not args.model_snapshot.is_dir():
            raise FileNotFoundError(f"Pinned model snapshot missing: {args.model_snapshot}")
        inputs_dir = args.manifest.parent / "inputs"

        load_started = time.perf_counter()
        processor = AutoProcessor.from_pretrained(args.model_snapshot, local_files_only=True)
        model = AutoModelForMultimodalLM.from_pretrained(
            args.model_snapshot,
            local_files_only=True,
            dtype=torch.float32,
            device_map={"": "cpu"},
            attn_implementation="eager",
        )
        model.eval()
        load_seconds = time.perf_counter() - load_started
        params = list(model.parameters())
        image_processor = processor.image_processor
        summary.update(
            {
                "status": "running",
                "load_seconds": load_seconds,
                "model_class": type(model).__name__,
                "processor_class": type(processor).__name__,
                "image_processor_class": type(image_processor).__name__,
                "model_device": str(params[0].device),
                "model_dtype": str(params[0].dtype),
                "parameter_count": sum(p.numel() for p in params),
                "preprocessing": {
                    key: str(getattr(image_processor, key, None))
                    for key in (
                        "size", "do_resize", "do_rescale", "rescale_factor",
                        "do_normalize", "image_mean", "image_std",
                    )
                },
                "cpu_rss_after_load_bytes": process.memory_info().rss,
            }
        )
        write_json(summary_path, summary)

        plan = [
            (args.image, "caption", CAPTION_PROMPT),
            (args.image, "water_qa", QUESTION_PROMPT),
            (args.second_image, "caption", CAPTION_PROMPT),
        ]
        succeeded = 0
        failed = 0
        with results_path.open("a", encoding="utf-8") as results_file:
            for opaque_file, task_name, prompt in plan:
                image_path, input_kind = load_image(inputs_dir, manifest, opaque_file)
                record: dict[str, Any] = {
                    "opaque_file": opaque_file,
                    "sha256": sha256_file(image_path),
                    "input_kind": input_kind,
                    "task": task_name,
                    "prompt": prompt,
                    "device": "cpu",
                    "started_at": datetime.now(UTC).isoformat(),
                }
                try:
                    with Image.open(image_path) as opened:
                        image = opened.convert("RGB")
                        record["source_image"] = {"mode": image.mode, "size_px": list(image.size)}
                        messages = [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image", "image": image},
                                    {"type": "text", "text": prompt},
                                ],
                            }
                        ]
                        preprocess_started = time.perf_counter()
                        raw = processor.apply_chat_template(
                            messages,
                            add_generation_prompt=True,
                            tokenize=True,
                            return_dict=True,
                            return_tensors="pt",
                        )
                        # Explicit CPU placement only; token tensors keep integer dtype.
                        inputs = {
                            k: (v.to("cpu") if isinstance(v, torch.Tensor) else v)
                            for k, v in raw.items()
                        }
                        record["preprocessing_seconds"] = time.perf_counter() - preprocess_started
                        record["tensors"] = tensor_summary(inputs)
                    input_tokens = inputs["input_ids"].shape[-1]
                    generation_started = time.perf_counter()
                    with torch.inference_mode():
                        generated_ids = model.generate(
                            **inputs, do_sample=False, max_new_tokens=args.max_new_tokens
                        )
                    record["generation_seconds"] = time.perf_counter() - generation_started
                    new_tokens = generated_ids[:, input_tokens:]
                    decoded = processor.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
                    record.update(
                        {
                            "status": "succeeded",
                            "input_token_count": input_tokens,
                            "output_token_count": new_tokens.shape[-1],
                            "output": decoded,
                            "cpu_rss_after_bytes": process.memory_info().rss,
                        }
                    )
                    succeeded += 1
                except Exception as error:  # noqa: BLE001
                    failed += 1
                    record.update(
                        {
                            "status": "failed",
                            "error_type": type(error).__name__,
                            "error": str(error),
                            "traceback": traceback.format_exc(),
                        }
                    )
                record["finished_at"] = datetime.now(UTC).isoformat()
                results_file.write(json.dumps(record, sort_keys=True) + "\n")
                results_file.flush()

        summary.update(
            {
                "status": "completed" if failed == 0 else "completed_with_failures",
                "successful_invocations": succeeded,
                "failed_invocations": failed,
                "finished_at": datetime.now(UTC).isoformat(),
                "elapsed_seconds": (datetime.now(UTC) - started_at).total_seconds(),
                "cpu_rss_final_bytes": process.memory_info().rss,
            }
        )
        write_json(summary_path, summary)
        return 0 if failed == 0 else 1
    except Exception as error:  # noqa: BLE001
        summary.update(
            {
                "status": "fatal_error",
                "error_type": type(error).__name__,
                "error": str(error),
                "traceback": traceback.format_exc(),
                "finished_at": datetime.now(UTC).isoformat(),
            }
        )
        write_json(summary_path, summary)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
