# Handoff: FIX-02 truthful implementation modes (backend lane)

- Status: needs review
- Worker, model/effort, workspace data classification: Sol (Muse Spark, this session);
  local integration repository; no restricted imagery, secrets, model data, or
  scientist correspondence accessed. Probe used a synthetic /tmp GeoTIFF only.
- Base commit and branch: `d13fd2c5d7a4d79286ccafee03c6eab52ce3dbb2`
  (`origin/main`, PR4 merged) on `sol/fix-02-truthful-modes`.
- Requirement and acceptance criteria: FIX-02 from
  SatQuery_Code_Review_and_Recovery_Plan.md + DEMO_EXECUTION_PLAN.md backend lane:
  scripted optical/SAR/temporal/fusion paths must not execute as real
  implementations; focused regressions prove the boundary; explicit mock mode
  preserved for labelled UI fixtures; missing real providers return honest
  MODEL_UNAVAILABLE. Retain all T01 checks.

## Files changed (backend only; no frontend files touched)

- `src/satquery/specialists/optical.py`, `sar.py`, `temporal.py`, `fusion.py`:
  CONTRACT `implementation="real"` -> `"mock"`; new keyword-only
  `scripted: bool = False` on `__init__`; `run()` keeps honest input validation
  (modality/temporal order) then raises `ValueError("MODEL_UNAVAILABLE: ...")`
  unless `scripted=True`. Scripted answers unchanged behind the opt-in.
- `src/satquery/controller/executor.py`: runner exceptions starting with
  `MODEL_UNAVAILABLE` map to `ToolError(code="MODEL_UNAVAILABLE")` instead of
  `INTERNAL`. All other exceptions still map to `INTERNAL`.
- `tests/test_truthful_modes.py` (new, 10 tests): contract flags are mock;
  default runs of all four specialists raise MODEL_UNAVAILABLE (incl. with a
  nonexistent `model_path`); `scripted=True` preserves the fixture output;
  real-mode `execute_plan` fails with MOCK_PROHIBITED; mock-mode plan with a
  scripted specialist succeeds; executor surfaces MODEL_UNAVAILABLE honestly.
- `tests/test_optical_specialist.py`, `test_sar_specialist.py`,
  `test_temporal_specialist.py`, `test_fusion_specialist.py`: former
  "successful_* as real" tests now run `scripted=True` and are renamed
  `*_labelled_fixture_*` (they asserted the requirement-violating behavior).
- `tests/test_controller.py`: `test_execute_plan_success` ->
  `test_execute_plan_succeeds_in_mock_fixture_mode` (mode="mock",
  scripted specialist); timeout test likewise uses mock mode so it still
  reaches the timeout block.

## What remains mock/unavailable

- All four specialists: real mode unavailable by design until a genuine
  provider is wired. Fixture path requires explicit `scripted=True` and
  `mode="mock"`.
- Real-model feasibility probe result: NO real optical VQA/caption execution
  established. Environment has an idle RTX 4050 (6 GB) but the locked venv
  contains no torch/transformers/PIL, no checkpoint, no model cache, and no
  permitted real imagery was supplied (repo has zero raster fixtures).
  No downloads, paid services, or licence acceptances were made (no task
  authorization). Demo checkpoint 2 stays 0/8.
- Pixel-plumbing probe (existing authorized resources only): wrote synthetic
  3x64x64 GeoTIFF to `/tmp/opencode/fix02-pixel-probe.tif`, decoded via
  `inspect_raster` (geotiff, band_1..3, 64x64, EPSG:32643), computed per-band
  means with numpy ([128.36, 126.26, 125.66]). Plumbing only; not VQA.

## Exact checks, exit codes, relevant output

All from `/home/aryan/satquery-core` with
`/home/aryan/.venvs/satquery-core-312/bin/python` (CPython 3.12.14):

- New gate first: `pytest tests/test_truthful_modes.py -q` -> 10 failed
  (reproduced against old behavior), then after fix -> part of 27 passed.
- `pytest tests/test_truthful_modes.py test_optical/sar/temporal/fusion/controller -q`
  -> 27 passed, exit 0.
- `python scripts/check.py` -> 42 unittest + 82 pytest + 5 subtests passed, exit 0.
- `python -m pytest -q` -> 82 passed, 3 known warnings, 5 subtests, exit 0.
- `python -m mypy` -> exit 0, 16 source files, no issues.
- `python scripts/export_schemas.py` + `git diff --exit-code -- schemas` -> exit 0.
- `ruff check` on all 11 changed/new files -> All checks passed, exit 0.
  (`ruff check .` repo-wide reports 46 findings, all inside untracked upload
  folders `.opencode/skills/`, `SatQuery_Review_and_Design_Package (1)/`,
  `SatQuery_Starter_Kit/`; none in tracked files; CI checks out tracked files
  only so it is unaffected. Upload folders are not staged.)

## PR URL, CI, uncommitted/untracked files

- Backend PR: to be opened from `sol/fix-02-truthful-modes` -> `main` after
  this handoff is committed; CI to be recorded there. Do not merge.
- Doc PR5 (separate branch `codex/demo-coordination`):
  https://github.com/compiledbyaryan/satquery-core/pull/5 , CI success, OPEN,
  do not merge automatically.
- Untracked reference uploads (kept local, never staged): the ZIP, recovery
  plan MD, review/design package dir, starter-kit dir, `Zone.Identifier`
  files, `.opencode/`, `.github/hooks/`.

## Startup, data/model assumptions, environment

- Backend checks run in the existing locked env; no new installs.
- No model weights, provider credentials, or real imagery assumed or added.
- Frontend lane untouched: no `apps/` paths exist or were created here.

## Known failures / checks not run

- Full GPU/model inference, raster exploit testing, browser/Playwright,
  security scans: not run (out of FIX-02 scope; no provider exists).
- FIX-03..FIX-08 defects from the recovery plan remain open by design.

## Immediate next action and decisions needed

1. Review + CI on the FIX-02 PR (this branch). Do not merge until reviewed.
2. Smallest next implementation for
   actual input -> model execution -> saved result -> HTTP retrieval:
   (a) FIX-03 minimal: align the one demo route's declared input slot names
   with runner signatures and resolve exact asset version identity
   (no full storage redesign); (b) authorize ONE real optical path only:
   choose an approved public/synthetic image + an installable open VLM that
   fits 6 GB VRAM (or a CPU fallback), record checkpoint/preprocessing, wire
   it as a new `implementation="real"` tool beside (not inside) the scripted
   fixtures; (c) FIX-07 minimal vertical slice on canonical routes already in
   code (`/api/v1/...` vs ADR-003 proposed `/v1/...` needs Sol's explicit
   canonical-route decision first), then publish runnable OpenAPI
   (`app.openapi()` JSON) and generate the TypeScript client inputs for the
   frontend seam. Until (b) succeeds, real mode honestly stays unavailable.
3. Decision needed from Aryan: which real image + model/provider is permitted
   (existing resources only, or authorize a specific bounded download/licence).

# Handoff: bounded SmolVLM / EuroSAT real-inference feasibility probe

- Status: blocked after two targeted failures; needs Sol review.
- Branch/worktree: `sol/smollm-eurosat-probe` in
  `/home/aryan/satquery-smollm-probe`.
- Base commit: `167f2c7b79affd8dc2ce661dfca08541cddcfdb9` (`origin/main` at branch
  creation).
- Scope: standalone optical inference proof only. No application code, API,
  specialist interface, test, schema, or locked core environment was changed.

## Authorized resources and retained provenance

- Official model: `HuggingFaceTB/SmolVLM-500M-Instruct`, Apache-2.0,
  revision `a7da5b986cb59b408707209984f360a5f4ad7e47`.
- Downloaded only JSON/text/README/Safetensors files. Optional ONNX files were
  excluded. `model.safetensors` is 1,015,025,832 bytes and SHA-256
  `d05b567eeaf534e83d375551f068ed57b5f52d37c657197f644af5ef9db091a2`.
- Official sample source: `timm/eurosat-rgb`, MIT, revision
  `b4e28552cd5f3932b6abc37eb20d3e84901ad728`, train split.
- Fixed sample: 12 rows at streaming indexes 0, 1350, ..., 14850, chosen before
  inference without label filtering. `manifest.json` retains identifiers,
  audit-only labels, hashes, source, split and license. The inference runner
  sees opaque filenames and in-memory PIL images only; prompts contain no class
  information. Acquisition/geospatial details remain unknown.
- Diagnostic: locally generated solid-gray 64x64 RGB `blank.png`, clearly
  distinguished from benchmark imagery.

## Environment and network budget

- Separate environment: `/home/aryan/.venvs/satquery-smollm-312`, CPython
  3.12.14. The core environment `/home/aryan/.venvs/satquery-core-312` was
  preserved.
- Key versions: accelerate 1.14.0, datasets 5.0.1, huggingface-hub 1.30.0,
  Pillow 12.3.0, psutil 7.2.2, torch 2.8.0, torchvision 0.23.0, transformers
  5.16.1. The full observed set is `environment.freeze.txt`.
- Preflight: 941 GiB filesystem free; RTX 4050 Laptop GPU, driver 592.82,
  6,141 MiB total and 5,920 MiB free.
- Download accounting: dependency logs named 3,615.5 MiB plus 60.0 MiB
  (rounded `uv` output); exact model-cache delta 1,020,010,311 bytes;
  corrective torchvision download 8.2 MiB. Conservatively adding the full
  documented 55.3 MB train parquet stays below 5.0 GB and the 8 GB budget.
  No second model, serving framework, paid/gated service, or account was used.

## Actual invocations and failures

The runner follows the publisher's AutoProcessor / AutoModelForMultimodalLM
chat-template flow and is configured for 26 deterministic invocations: caption
and water-presence Q&A on 12 benchmark images plus the blank diagnostic. It
records prompt/output/failure, preprocessing, latency, tensors, process RSS and
GPU memory evidence as stages are reached.

1. `results/run_20260908/run_summary.json`: processor construction
   failed because Transformers 5.16.1 required optional `torchvision`. No image
   invocation record exists because failure occurred before the loop. The outer
   WSL command reported exit 1; the runner recorded `fatal_error` and is coded
   to return 2 for a fatal setup failure.
2. Installed only compatible `torchvision==0.23.0` (8.2 MiB), then
   `results/run_20260908_retry1/run_summary.json`: processor loaded, but
   model load failed during allocator warm-up with CUDA OOM while attempting a
   966 MiB allocation. The outer WSL command again reported exit 1.
   `nvidia-smi` had reported 4.95 GiB free. The backend's
   impossible `17179869184.00 GiB` non-PyTorch-memory figure is retained
   verbatim and must not be treated as a measurement.

Recorded UTC timestamps give elapsed times of 0.600476 seconds and 21.714641
seconds. Pre-load process RSS was 718,913,536 and 725,344,256 bytes. Both
pre-load GPU snapshots reported 0 MiB used and 5,920 MiB free. No trustworthy
post-failure memory sample or image-preprocessing latency was produced.

The requested two-failure stop was observed. No image reached preprocessing or
generation, so there are no captions, Q&A answers, blank-image comparison,
latencies, or peak generation memory to report. This does not complete the
real-imagery checkpoint and provides no scientific-accuracy evidence.

## Runnable command

```bash
cd /home/aryan/satquery-smollm-probe
TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false \
  /home/aryan/.venvs/satquery-smollm-312/bin/python \
  evaluation/optical/smollm-eurosat/run_probe.py \
  --manifest evaluation/optical/smollm-eurosat/manifest.json \
  --output-dir evaluation/optical/smollm-eurosat/results/NEW_RUN \
  --max-new-tokens 48
```

Output directories are immutable: the runner refuses to overwrite one. Keep
both existing failed-run summaries.

## Smallest next step and decision for Sol

Reproduce the load failure using the same pinned local model and inspect why
Transformers 5.16.1 / Torch 2.8.0 allocator warm-up fails on this WSL/CUDA
combination. Decide whether a publisher-supported lower-memory setting—an
explicit dtype/device map or CPU execution—is acceptable for this feasibility
checkpoint. Do not download a quantizer, another checkpoint, or a serving
framework without new authorization.

Only after a standalone image produces persisted caption/Q&A evidence should a
small adapter be considered: accept decoded RGB pixels, invoke the processor and
model service, and return text plus model revision/evidence. Keep it separate
from scripted fixtures; the current optical specialist remains truthfully
unavailable in real mode.


# Addendum: CPU rescue succeeded — one caption + one answer (2026-09-08)

- Status: first real-inference evidence obtained; checkpoint 2 partially evidenced
  (single image, not a validated capability).
- Rescue env/settings: `/home/aryan/.venvs/satquery-smollm-312`, CUDA hidden
  (`CUDA_VISIBLE_DEVICES=""`, `torch.cuda.is_available()=False`), CPU float32,
  `attn_implementation="eager"`, `local_files_only` on pinned revision
  `a7da5b98...`, eval + `inference_mode`, batch 1, 24 new tokens, greedy.
- Diagnosed cause of prior failures: (1) Transformers 5.16.1 Idefics3 processor
  needed `torchvision` (fixed by installing pinned `torchvision==0.23.0`);
  (2) `device_map="auto"` triggered CUDA allocator warm-up OOM on the 6 GiB
  RTX 4050. CPU placement avoids both. Prior failure records preserved.
- New code: `evaluation/optical/smollm-eurosat/run_rescue.py` (CPU-only,
  writes a NEW run dir, never overwrites `run_20260908*`).
- New evidence: `evaluation/optical/smollm-eurosat/results/run_20260908_cpu/`
  (`run_summary.json` + `invocations.jsonl`, ~12 KB, status `completed`, 3/3).
- Actual generations (sample_01, hash `916c3b69...`, row 0):
  - caption: "A blurry image of a building with a person in a dark shirt."
    (pre 5.43 s, gen 89.63 s, 1166 in / 15 out tokens)
  - water_qa: "No." (pre 1.52 s, gen 56.24 s, 1162 in / 3 out tokens)
  - blank caption: "A grey background with no text or objects."
    (pre 0.70 s, gen 38.64 s, 1166 in / 10 out tokens)
  Model: `Idefics3ForConditionalGeneration`, 507,482,304 params, CPU float32,
  load 10.3 s, total run 203 s. Preprocessing: resize (longest edge 2048),
  rescale 1/255, normalize mean/std (0.5, 0.5, 0.5).
- Quality note (execution != accuracy): the audit label for sample_01 is
  PermanentCrop (field pattern), yet the caption claims "a building with a
  person" — a hallucination on 64x64 satellite pixels. The water answer "No."
  is terse and unvalidated. Differing answers across images must not be
  presented as scientific accuracy. Blank diagnostic behaves sanely.
- Reusable command:
  `CUDA_VISIBLE_DEVICES="" TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1
  TOKENIZERS_PARALLELISM=false /home/aryan/.venvs/satquery-smollm-312/bin/python
  evaluation/optical/smollm-eurosat/run_rescue.py --manifest
  evaluation/optical/smollm-eurosat/manifest.json --output-dir
  evaluation/optical/smollm-eurosat/results/<NEW_RUN> --max-new-tokens 24`
- Smallest adapter step for Sol: wrap `run_rescue.py`'s load/infer sequence as
  a standalone `implementation="real"` optical tool that accepts decoded RGB
  pixels + question, runs the pinned CPU path above, and returns text plus
  model revision/input hash/evidence. Keep scripted fixtures untouched.
