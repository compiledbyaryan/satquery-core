"""Run an offline, evidence-preserving SmolVLM feasibility probe."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
import torch
from PIL import Image
from transformers import AutoModelForMultimodalLM, AutoProcessor

MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"
MODEL_REVISION = "a7da5b986cb59b408707209984f360a5f4ad7e47"
DEFAULT_SNAPSHOT = Path(
    "/home/aryan/.cache/huggingface/hub/"
    "models--HuggingFaceTB--SmolVLM-500M-Instruct/snapshots/"
    f"{MODEL_REVISION}"
)
TASKS = {
    "caption": (
        "Describe the visible scene in one concise sentence. Mention only features visible "
        "in the image; do not infer location, date, sensor, or physical measurements."
    ),
    "water_qa": (
        "Does this image appear to contain a large body of water? Answer yes, no, or "
        "uncertain, then give one short visual reason."
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model-snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=48)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return str(value)


def gpu_snapshot() -> dict[str, str] | None:
    if not torch.cuda.is_available():
        return None
    command = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,memory.used,memory.free",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    name, driver, total, used, free = [part.strip() for part in completed.stdout.split(",")]
    return {
        "name": name,
        "driver_version": driver,
        "memory_total_mib": total,
        "memory_used_mib": used,
        "memory_free_mib": free,
    }


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


def main() -> int:
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
            for name in (
                "torch",
                "torchvision",
                "transformers",
                "Pillow",
                "psutil",
                "huggingface-hub",
            )
        },
        "gpu_before_load": gpu_snapshot(),
        "cpu_rss_before_load_bytes": process.memory_info().rss,
    }
    write_json(summary_path, summary)

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if manifest["n_samples"] > 12:
            raise ValueError("Probe is limited to at most 12 benchmark images")
        if not args.model_snapshot.is_dir():
            raise FileNotFoundError(f"Pinned model snapshot missing: {args.model_snapshot}")
        inputs_dir = args.manifest.parent / "inputs"
        benchmark_inputs = []
        for sample in manifest["samples"]:
            opaque_file = sample["opaque_file"]
            if not opaque_file.startswith("sample_"):
                raise ValueError(f"Inference filename is not opaque: {opaque_file}")
            image_path = inputs_dir / opaque_file
            actual_hash = sha256_file(image_path)
            if actual_hash != sample["sha256"]:
                raise ValueError(f"Hash mismatch for {opaque_file}")
            benchmark_inputs.append((opaque_file, actual_hash, image_path))
        diagnostic = manifest["diagnostic"]
        diagnostic_path = inputs_dir / diagnostic["opaque_file"]
        if sha256_file(diagnostic_path) != diagnostic["sha256"]:
            raise ValueError("Hash mismatch for blank diagnostic")

        load_started = time.perf_counter()
        processor = AutoProcessor.from_pretrained(
            args.model_snapshot,
            local_files_only=True,
        )
        model = AutoModelForMultimodalLM.from_pretrained(
            args.model_snapshot,
            device_map="auto",
            local_files_only=True,
        )
        model.eval()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        load_seconds = time.perf_counter() - load_started
        model_device = next(model.parameters()).device
        image_processor = processor.image_processor
        summary.update(
            {
                "status": "running",
                "load_seconds": load_seconds,
                "model_class": type(model).__name__,
                "processor_class": type(processor).__name__,
                "model_device": str(model_device),
                "model_dtype": str(next(model.parameters()).dtype),
                "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
                "preprocessing": {
                    key: json_value(getattr(image_processor, key, None))
                    for key in (
                        "size",
                        "do_resize",
                        "do_rescale",
                        "rescale_factor",
                        "do_normalize",
                        "image_mean",
                        "image_std",
                    )
                },
                "gpu_after_load": gpu_snapshot(),
                "torch_cuda_after_load_bytes": {
                    "allocated": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
                    "reserved": torch.cuda.memory_reserved() if torch.cuda.is_available() else 0,
                },
                "cpu_rss_after_load_bytes": process.memory_info().rss,
                "planned_invocations": len(benchmark_inputs) * len(TASKS) + len(TASKS),
            }
        )
        write_json(summary_path, summary)

        invocations = [
            (opaque_file, image_hash, image_path, "benchmark")
            for opaque_file, image_hash, image_path in benchmark_inputs
        ]
        invocations.append(
            (
                diagnostic["opaque_file"],
                diagnostic["sha256"],
                diagnostic_path,
                "blank_diagnostic",
            )
        )

        succeeded = 0
        failed = 0
        with results_path.open("a", encoding="utf-8") as results_file:
            for opaque_file, image_hash, image_path, input_kind in invocations:
                for task_name, prompt in TASKS.items():
                    record: dict[str, Any] = {
                        "opaque_file": opaque_file,
                        "sha256": image_hash,
                        "input_kind": input_kind,
                        "task": task_name,
                        "prompt": prompt,
                        "started_at": datetime.now(UTC).isoformat(),
                    }
                    try:
                        with Image.open(image_path) as opened:
                            image = opened.convert("RGB")
                            record["source_image"] = {
                                "mode": image.mode,
                                "size_px": list(image.size),
                            }
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
                            inputs = processor.apply_chat_template(
                                messages,
                                add_generation_prompt=True,
                                tokenize=True,
                                return_dict=True,
                                return_tensors="pt",
                            )
                            record["preprocessing_seconds"] = (
                                time.perf_counter() - preprocess_started
                            )
                            record["tensors_before_device_move"] = tensor_summary(inputs)
                            inputs = inputs.to(model_device)

                        input_tokens = inputs["input_ids"].shape[-1]
                        if torch.cuda.is_available():
                            torch.cuda.reset_peak_memory_stats()
                            torch.cuda.synchronize()
                        generation_started = time.perf_counter()
                        with torch.inference_mode():
                            generated_ids = model.generate(
                                **inputs,
                                do_sample=False,
                                max_new_tokens=args.max_new_tokens,
                            )
                        if torch.cuda.is_available():
                            torch.cuda.synchronize()
                        record["generation_seconds"] = (
                            time.perf_counter() - generation_started
                        )
                        generated_tokens = generated_ids[:, input_tokens:]
                        decoded = processor.batch_decode(
                            generated_tokens,
                            skip_special_tokens=True,
                        )[0].strip()
                        record.update(
                            {
                                "status": "succeeded",
                                "tensors_after_device_move": tensor_summary(inputs),
                                "input_token_count": input_tokens,
                                "output_token_count": generated_tokens.shape[-1],
                                "output": decoded,
                                "cpu_rss_after_bytes": process.memory_info().rss,
                                "gpu_after": gpu_snapshot(),
                                "torch_cuda_peak_allocated_bytes": (
                                    torch.cuda.max_memory_allocated()
                                    if torch.cuda.is_available()
                                    else 0
                                ),
                                "torch_cuda_peak_reserved_bytes": (
                                    torch.cuda.max_memory_reserved()
                                    if torch.cuda.is_available()
                                    else 0
                                ),
                            }
                        )
                        succeeded += 1
                    # Evidence preservation requires recording unexpected backend errors too.
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
                "gpu_final": gpu_snapshot(),
            }
        )
        write_json(summary_path, summary)
        return 0 if failed == 0 else 1
    # Preserve fatal setup/load failures in the run summary before exiting.
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
