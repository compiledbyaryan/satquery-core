# Validation record

Verified in the authoring environment on 6 September 2026 (UTC research snapshot):

- Python 3.12, Pydantic 2.13.4.
- 42 unittest checks passed through `python scripts/check.py`.
- Seven JSON Schemas exported from the final contract definitions.
- An independent review identified named input/output binding gaps, blank-string acceptance and determinant-overflow behaviour. These were repaired with regression coverage.

The suite covers structural records, named bindings, asset compatibility guards, temporal ordering, affine arithmetic, Boolean change counts and dependency invalidation. It does not run a spatial model or establish scientific answer accuracy.

Not run: clean dependency installation, pytest execution, Ruff, mypy, remote CI, browser tests, database concurrency, isolated raster decoding, model inference, training, deployment or end-to-end application tests. T01 establishes the missing environment gates; later tickets establish their feature gates. No lockfile is supplied before a real dependency resolution.

The included workflow is a proposed baseline CI configuration, not evidence that GitHub Actions ran. A schema is an interface, not proof that its data describes reality. No API, UI or application server is delivered in this starter.
