# Handoff: T01 mypy cleanup

- Status: needs review; mypy portion implemented and locally verified
- Worker, model/effort, workspace data classification: Codex; local integration repository;
  no restricted imagery, secrets, model data, or scientist correspondence accessed
- Base commit and branch: `83f96cea2394d61ee86433e6415aef6b2b30c1d6` on
  `codex/t01-mypy-cleanup`
- Requirement and acceptance criteria: resolve strict mypy findings without weakening
  configuration or behavior, add mypy to the locked CI job, retain Ruff/tests/schema checks,
  and assess every T01 acceptance criterion
- Public contract changes: none; HTTP response schemas and JSON remain unchanged
- Browser screenshots or sample artifacts, if relevant: not applicable
- Data/model licences and fixture provenance: no data, model, dependency, or fixture added
- Conflicts or decisions required: none
- Next unblocked ticket: T02 according to `docs/TICKETS.md`, after review and merge; no later
  ticket work was started here

## Baseline and root causes

The configured strict mypy run exited 1 with 25 errors in nine source files. They grouped
into five root causes rather than 25 independent defects:

1. Twelve errors came from missing return annotations and the resulting untyped constructor
   calls, including six FastAPI route functions.
2. Two storage methods promised a record but returned the optional result of a follow-up
   lookup without checking it.
3. Four temporal-specialist errors reused optional acquisition timestamps after a validator
   call whose narrowing mypy cannot observe.
4. Four ingestion errors came from Rasterio's missing typing metadata and broad strings at
   the driver/modality boundary.
5. Three controller errors came from an unnecessarily broad error-code variable and a
   heterogeneous keyword dictionary inferred from its first value.

## Files changed and behavior

- `.github/workflows/contracts.yml`: run strict mypy in the existing locked `checks` job.
- `docs/START_HERE.md`: include the mypy command in both supported setup sequences.
- `docs/STATUS.md`: record local T01 acceptance and pending review/CI/merge.
- `docs/T01_MYPY_HANDOFF.md`: this verification record.
- `src/satquery/storage/jobs.py`, `src/satquery/evidence/store.py`, and
  `src/satquery/controller/registry.py`: add accurate `None` return annotations and explicit
  checks for impossible missing rows after successful storage writes.
- `src/satquery/specialists/temporal.py`: narrow required timestamps through real checks and
  use the narrowed locals.
- `src/satquery/ingestion/inspector.py`: type the modality contract, validate the untrusted
  Rasterio driver through a literal mapping, and isolate Rasterio's absent `py.typed` marker
  with two line-specific `import-untyped` annotations.
- `src/satquery/controller/executor.py`: preserve the existing `UNSUPPORTED` result directly
  and accurately type the heterogeneous runner argument dictionary as `dict[str, object]`.
- `src/satquery/api/feedback.py` and `src/satquery/api/routes.py`: add return annotations and
  validate storage-derived response data with existing Pydantic response models.

The HTTP tests confirm unchanged serialized responses and authorization behavior. No tests,
assertions, strict settings, dependencies, or schema contracts were changed. No `Any`, cast,
blanket ignore, source exclusion, or unchecked Pydantic construction was added.

## Exact checks and acceptance assessment

All Python commands used the existing `/home/aryan/.venvs/satquery-core-312` environment,
which resolves separately from the repository `.venv` and reports CPython 3.12.14. It was
not recreated or synchronized during this work.

- Baseline `python -m mypy`: exit 1, 25 errors in nine files.
- Final `python -m mypy`: exit 0, 16 source files checked.
- `python -m ruff check .`: exit 0.
- `python scripts/check.py`: exit 0; 42 unittest tests passed, then 72 pytest tests and five
  subtests passed with three warnings.
- `python -m pytest --collect-only -q`: exit 0; 72 tests collected, including all 42 unittest
  methods plus 30 pytest-style functions.
- `python scripts/export_schemas.py`: exit 0.
- `git diff --exit-code -- schemas`: exit 0 after export; no schema drift.
- Schema-drift canary: a temporary `x-drift-canary` field was added to
  `schemas/AssetRecord.json`; the exact `git diff --exit-code -- schemas` command exited 1.
  The same patch was reversed, the file's Git blob hash returned to
  `8bf56a8bb8bc2f87b6fe510536bcaeaec644335d`, and no canary file remains.
- `UV_PROJECT_ENVIRONMENT=/home/aryan/.venvs/satquery-core-312 uv sync --check --locked
  --extra dev --python 3.12`: exit 0 and would make no changes.
- `uv pip check --python /home/aryan/.venvs/satquery-core-312/bin/python`: exit 0; 31 packages
  checked and compatible.
- `git diff --exit-code -- uv.lock`: exit 0; the lock is unchanged.

The earlier accepted environment repair created and verified the clean locked Python 3.12
environment. This turn verified and reused it; it did not repeat a clean installation.
Together with the current test collection, clean schema export, drift canary, Ruff pass, and
mypy pass, every stated T01 acceptance criterion has local evidence. GitHub CI and review
remain pending until this branch is published.

## Known limitations and checks not run

The gate still emits three known dependency/runtime warnings: FastAPI's deprecated
httpx/TestClient integration, Starlette's deprecated AnyIO `BlockingPortal` alias, and
Rasterio's pending deprecation of affine `*` multiplication. The uv-managed environment
does not contain the `pip` module, so `python -m pip check` exited 1; the supported
`uv pip check` command passed instead. No clean environment was rebuilt, no application or
scientific correctness was certified, and no subsequent ticket was started.
