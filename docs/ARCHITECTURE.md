# Architecture and integration contract

## ADR-001: modular monolith with isolated workers
Use one Python application codebase plus a React/TypeScript UI. Deploy API and worker as separate processes from the same project. Isolate heavy model environments when dependencies conflict. Do not split into independently evolving business microservices, introduce a broker fleet or require Kubernetes.

Planned modules: `src/satquery/api/`, `storage/`, `ingest/`, `jobs/`, `specialists/`, `controller/`, `evidence/`, `evaluation/`. Current `contracts.py` and `validation.py` are the initial shared foundation. `apps/web/` is reserved for UI. Pure domain logic must not import web routes or React concepts.

Use FastAPI; Python 3.12 core; Pydantic v2; a SQLite job/artifact store for the single-host pilot; SQL migrations owned by the integrator; local object files behind an ArtifactStore interface. A dedicated worker claims jobs transactionally with a lease and heartbeat. One GPU job at a time initially. Move to PostgreSQL or an external queue only when concurrency and deployment require it. Older model repositories may use separate Python/CUDA containers.

## ADR-002: contracts before consumers
Authoritative schemas live in `src/satquery/contracts.py`, generated exports in `schemas/`. Model adapters implement `Specialist.execute(params: ToolParams, context: ToolContext) -> ToolResult`. Named input slots and named outputs are mandatory; two masks cannot be distinguished only by kind. `OutputInput.output_name` resolves a producer's `NamedOutput.name`.

The current schemas are structural. Remaining runtime obligations: authenticate caller; validate actual raster/product metadata; resolve versions and artifact ownership; verify each registry task and parameter against the selected tool; check paired coverage/registration; validate output names/kinds; record real execution; determine claim acceptance from actual evidence. Do not accept worker-supplied `supported` status as the final decision.

## ADR-003: HTTP contract is the first integration ticket
T02 creates transport records and OpenAPI; until merged, UI uses isolated prototype fixtures and no invented live endpoints. Proposed surface:
- POST `/v1/assets` upload; GET `/v1/assets/{id}` metadata; GET `/v1/assets/{id}/preview`.
- POST `/v1/runs` with query, exact asset versions and Idempotency-Key; return 202 plus run ID.
- GET `/v1/runs/{id}`; GET `/v1/runs/{id}/events?after_sequence=N`.
- POST `/v1/runs/{id}/cancel`; GET `/v1/runs/{id}/claims`.
- GET `/v1/artifacts/{id}` and authorised tile routes.
- POST `/v1/runs/{id}/revisions`; GET `/v1/reports/{id}`.

Job states: queued -> validating -> running -> verifying -> succeeded/partial/failed/cancelled. Terminals never regress. Cancellation is cooperative at checkpoints; process termination after timeout must not publish partial files. Same idempotency key+same body returns same run; same key+different body returns 409. Scope keys by user and endpoint; expire by documented policy. Use unique database constraints and atomic transactions, not a dictionary in a web process. Polling first; SSE later if valuable.

API errors are a typed envelope with code, message, request ID and optional safe field errors. Avoid raw stack traces and storage paths. Mock providers exist only in explicit test/demo configuration. Real mode must fail if a real provider is unavailable.

## ADR-004: immutable artifacts and selective replay
Store immutable asset versions and outputs. Cache identity includes relevant input hashes, model/weights digest, code/contract version, preprocessing, AOI, grid, dates, parameters, seed and determinism policy. Never cache by filename or prompt alone. Resolve changed OLD versions in the existing graph before creating replacements. Invalidate descendants and claims first, rerun dependencies, and compare with a clean rerun. Deleted or inaccessible parents produce an unresolved provenance error.

All draft, cache-hit, failed and partial outputs retain their status. Checks use pass/fail/unknown/not-applicable; required checks cannot pass by being marked not-applicable. Hashes prove consistency relationships only.

## ADR-005: data boundaries
Raw/hidden/scientist data never enters Contributor workspaces. Use a fresh sanitised repository or export with only approved files and no private Git history. After implementation, the integrator imports a reviewed patch. The main repository remains authoritative. Do not use Dropbox/OneDrive folder synchronization as Git coordination.

Every upload is decoded in a restricted process with allowed drivers, no credentials/network, generated filenames and byte/dimension/band/time limits. Reject VRT, arbitrary paths/URLs and executable raster expressions in this release. Apply access checks to tiles, artifacts, reports and jobs, not only creation.

