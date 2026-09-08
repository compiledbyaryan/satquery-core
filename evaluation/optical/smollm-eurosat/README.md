# SmolVLM / EuroSAT feasibility probe

This directory records a bounded real-inference attempt. It is not a scientific
validation and it does not make any SatQuery specialist a real implementation.

## Status

Incomplete after the requested two targeted attempts. No image reached
generation, so neither image Q&A nor captioning produced an answer. The two
failures are preserved under `results/`:

- `run_20260908`: processor setup failed because `torchvision` was absent.
- `run_20260908_retry1`: after installing compatible `torchvision==0.23.0`,
  model loading failed during CUDA allocator warm-up on the 6 GiB GPU.

The runner preserves every per-image output if generation starts, but both
failures occurred before the invocation loop. The blank-image diagnostic was
therefore scheduled but not executed. This is actual model invocation evidence,
not a completed real-imagery checkpoint.

## Provenance

- Model: `HuggingFaceTB/SmolVLM-500M-Instruct`, official publisher
  HuggingFaceTB, Apache-2.0, revision
  `a7da5b986cb59b408707209984f360a5f4ad7e47`.
- Model weights: `model.safetensors`, 1,015,025,832 bytes, SHA-256
  `d05b567eeaf534e83d375551f068ed57b5f52d37c657197f644af5ef9db091a2`.
- Only Transformers files were downloaded; optional ONNX variants were excluded.
- Dataset: `timm/eurosat-rgb`, MIT, revision
  `b4e28552cd5f3932b6abc37eb20d3e84901ad728`, train split.
- Sample: 12 deterministic streamed rows selected by fixed stride without label
  filtering, plus one locally generated gray diagnostic. The 13 PNGs total
  70,657 bytes. `manifest.json` records row identifiers, audit-only source IDs
  and label IDs, hashes, source, split, and license.
- Inference paths and prompts use only opaque names (`sample_NN.png` and
  `blank.png`). Source labels and IDs are never passed to the processor.
- Acquisition time and geospatial metadata are absent from this mirror and
  remain unknown.

Upstream records:

- https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct
- https://huggingface.co/datasets/timm/eurosat-rgb

`fetch_sample.py` pins the dataset revision and reproduces the fixed selection.

## Environment and download ledger

The separate environment is `/home/aryan/.venvs/satquery-smollm-312` using
CPython 3.12.14. The locked core environment
`/home/aryan/.venvs/satquery-core-312` was not changed. Exact installed package
versions are in `environment.freeze.txt`.

Preflight showed 941 GiB free on the WSL filesystem and 5,920 MiB free of
6,141 MiB GPU memory. The official model tree was inspected before download;
the selected Transformers snapshot was about 1.02 GB versus 6.9 GB for the tree
including excluded ONNX variants.

Observed network accounting:

- Initial dependency log named 3,615.5 MiB of downloads (rounded `uv` output),
  dominated by Torch/CUDA packages.
- Dataset dependencies named 60.0 MiB (rounded `uv` output).
- Model Hugging Face cache delta was exactly 1,020,010,311 bytes.
- The corrective `torchvision==0.23.0` download was 8.2 MiB (rounded `uv`
  output).
- EuroSAT's documented train parquet is 55.3 MB; streaming transfer bytes were
  not instrumented, so this is retained as a conservative upper bound rather
  than claimed as measured traffic.

Even summing the rounded dependency downloads, exact model delta, and the full
55.3 MB train parquet upper bound is under 5.0 GB, below the authorized 8 GB.
No other model was downloaded.

The corrective install command was:

```bash
/home/aryan/.local/bin/uv pip install \
  --python /home/aryan/.venvs/satquery-smollm-312/bin/python \
  torchvision==0.23.0
```

## Runnable inference command

The exact retry command was:

```bash
cd /home/aryan/satquery-smollm-probe
TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
  /home/aryan/.venvs/satquery-smollm-312/bin/python \
  evaluation/optical/smollm-eurosat/run_probe.py \
  --manifest evaluation/optical/smollm-eurosat/manifest.json \
  --output-dir evaluation/optical/smollm-eurosat/results/NEW_RUN \
  --max-new-tokens 48
```

The runner pins the local model revision, verifies all input hashes, uses the
publisher's `AutoProcessor` / `AutoModelForMultimodalLM` chat-template flow,
passes in-memory RGB PIL images, and requests deterministic generation. It
records preprocessing tensor shape/dtype/device, preprocessing and generation
latency, token counts, process RSS, `nvidia-smi` snapshots, and Torch CUDA
allocated/reserved peaks when those stages are reached.

## Observed failures and next bounded step

Attempt 1 failed before model load with a missing optional `torchvision`
processor backend. Attempt 2 loaded the processor, then failed while loading the
model: Transformers' allocator warm-up tried to allocate 966 MiB and raised CUDA
OOM despite `nvidia-smi` reporting 4.95 GiB free. The exception message's
non-PyTorch-memory figure (`17179869184.00 GiB`) is internally inconsistent and
is preserved verbatim in the run summary rather than interpreted as real use.
From the recorded UTC timestamps, attempts 1 and 2 lasted 0.600476 and
21.714641 seconds respectively. Their recorded pre-load process RSS values were
718,913,536 and 725,344,256 bytes. Both pre-load GPU snapshots reported 0 MiB
used and 5,920 MiB free; no trustworthy post-failure GPU sample was produced.
No image preprocessing occurred, so preprocessing latency is unavailable.

The smallest adapter integration step, only after a successful standalone run,
is a new optical provider that accepts decoded RGB pixels, calls this processor
and model service, and returns its text plus model revision and evidence fields.
Keep it separate from scripted fixtures and leave the existing real specialist
unavailable until the standalone probe succeeds.

Sol's next bounded investigation should reproduce the load failure and decide
whether a publisher-supported lower-memory load setting (for example an explicit
dtype/device map or CPU execution) is acceptable. It must use the same model and
must not download a quantizer, second checkpoint, or serving framework without
new authorization.
