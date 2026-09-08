# Integrator-owned status

Baseline: contract starter 0.1.0, 42 checks passing through unittest on Python 3.12 / Pydantic 2.13.4.
No model runs, training, API server, GUI or deployment exists in this package.
No GitHub repository is connected or modified by this delivery.

Current gate: T01 clean environment and development checks, T02 transport contract.
Do not assign integration-dependent tickets until their dependencies are merged.
Contributor boundary: not provisioned yet. Sanitise before handing out a workspace.

Only the integrator updates this summary. Workers append their own handoff file instead of racing to edit shared status.

## Test-discovery repair

The verification gate retains the 42-test unittest baseline and now also runs the full
72-test pytest suite, propagating pytest failures. A clean uv-locked environment was
verified with CPython 3.12.14: dependency checks, the full gate, and schema stability pass.
Ruff and strict mypy now pass and run in the locked CI checks job. All T01 acceptance
criteria have been demonstrated locally on the T01 branch, including a reversible schema
drift canary that made the CI diff command fail before exact restoration. The accepted
clean-environment repair established the Python 3.12 installation; this cleanup reused
that verified environment rather than recreating it. T01 remains pending review, GitHub
CI, and merge. Passing these development checks does not certify application or
scientific correctness.

## Final demo frontend integration — 2026-09-08

The historical starter statements above are superseded for frontend status by
`docs/handoffs/demo-completion.md`. The workbench now completes an explicitly labelled
synthetic fixture submission through result, matching evidence, reset, and JSON export.
Recorded CPU inference remains separately labelled and unchanged. Both independent apps
build; 20 frontend tests and 46 real-browser checks pass, along with the existing Python
baseline. No live UI/backend inference route or scientific acceptance completion is claimed.
Feature branch: `codex/demo-completion`; review required, no automatic merge.
