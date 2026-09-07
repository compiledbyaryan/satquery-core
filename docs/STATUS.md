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
72-test pytest suite, propagating pytest failures. This was verified with Python 3.14.4,
not Python 3.12. T01 remains incomplete: a clean Python 3.12 setup, a dependency lock,
and Ruff/mypy cleanup are pending. Passing 72 tests does not certify application or
scientific correctness.
