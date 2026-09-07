# Handoff: T01 environment and dependency lock
- Status: needs review; environment portion verified, T01 lint/type cleanup remains
- Worker, model/effort, workspace data classification: Codex; local existing repository
- Base commit and branch: `bfc2c383bf68d07ce7ff183dcd1c606cc9d671f4`; `codex/t01-environment`
- Requirement and acceptance criteria: resolve and lock declared dependencies with Python 3.12, verify the full gate and schema stability, and record Ruff/mypy without changing application logic
- Files changed: `uv.lock`, `.github/workflows/contracts.yml`, `docs/START_HERE.md`, `docs/STATUS.md`, this handoff
- Behaviour implemented: uv lock/sync workflow; CI installs uv 0.12.10, syncs the locked dev extra on Python 3.12, and runs the existing gate and schema export through that environment
- Public contract changes: none
- Data/model licences and fixture provenance: no data, model, or new fixture introduced

## Historical environment-repair setup

These commands record what ran during that repair; use `START_HERE.md` for current setup.

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/satquery-uv-install.sh
sh /tmp/satquery-uv-install.sh
uv python install 3.12
uv lock --python 3.12 --managed-python
uv venv /home/aryan/.venvs/satquery-core-312 --python 3.12 --managed-python
UV_PROJECT_ENVIRONMENT=/home/aryan/.venvs/satquery-core-312 uv sync --extra dev --locked
```

uv 0.12.10 installed CPython 3.12.14 and resolved 32 packages. The lock selected
mypy 1.20.2, preserving the declared `mypy>=1.15,<2` constraint.

## Exact verification

- `uv lock --check --python 3.12 --managed-python`: exit 0.
- `UV_PROJECT_ENVIRONMENT=/home/aryan/.venvs/satquery-core-312 uv sync --check --extra dev --locked`: exit 0; no changes.
- `uv pip check --python /home/aryan/.venvs/satquery-core-312/bin/python`: exit 0; 31 installed packages compatible.
- `/home/aryan/.venvs/satquery-core-312/bin/python scripts/check.py`: exit 0; 42 unittest tests and 72 pytest tests passed, plus 5 subtests.
- `uv sync --locked --extra dev --python 3.12`: exit 0; CI-equivalent project environment is synchronized.
- `uv run --locked --extra dev python scripts/check.py`: exit 0; same 42 unittest and 72 pytest results.
- `uv run --locked --extra dev python scripts/export_schemas.py`: exit 0.
- `/home/aryan/.venvs/satquery-core-312/bin/python scripts/export_schemas.py`: exit 0.
- `git diff --exit-code -- schemas`: exit 0; no schema drift.
- `python -m ruff check . --statistics`: exit 1; 130 errors (111 automatically fixable). Largest groups: UP006 33, UP045 27, UP017 23, I001 16, UP035 15, F401 9; seven other rules report one each.
- `python -m mypy`: exit 1; 25 errors in 9 files. Counts by file: storage/jobs.py 5, ingestion/inspector.py 4, specialists/temporal.py 4, controller/executor.py 3, api/feedback.py 3, api/routes.py 3, evidence/store.py 1, controller/registry.py 1, reports/builder.py 1.

Warnings from pytest: Starlette's httpx TestClient path is deprecated; AnyIO's
`BlockingPortal` alias is deprecated; Rasterio's affine multiplication emits a pending
deprecation warning.

## Known limitations and incident

T01 is not complete until the existing Ruff and mypy findings are repaired and their
gates can be enabled. Passing tests do not certify application or scientific correctness.

During setup, `uv sync --python /home/aryan/.venvs/satquery-core-312/bin/python`
unexpectedly replaced the ignored project `.venv` instead of targeting the separate
environment. This violated the requirement to preserve the previous Python 3.14
environment until replacement verification. The prior environment cannot be restored
from Git. No tracked file was lost. The command was not repeated; the supported
`UV_PROJECT_ENVIRONMENT` setting was then used to sync and verify the separate
environment.

- Conflicts or decisions required: review the uv workflow and decide whether lint and type cleanup should be split into a follow-up T01 repair.
- Next unblocked ticket: T01 Ruff/mypy cleanup; do not mark T01 complete yet.
