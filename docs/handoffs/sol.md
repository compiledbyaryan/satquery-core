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
