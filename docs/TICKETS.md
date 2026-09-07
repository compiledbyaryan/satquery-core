# Sequenced tickets

T00 is complete: the delivered structural contract foundation and 42 baseline tests. All tickets below are pending. Interface signatures below are proposed seams for their owner to implement and publish; consumers must wait for a merged implementation. Test files named below are to be created by the ticket owner, not claimed to exist already. Write one focused failing behaviour test, implement it, then repeat. Use exact expected values below plus valid controls. Split a ticket if it becomes several independent behaviours; do not send a 140k-token assignment.

Each handoff includes base SHA, file scope, actual checks, limitations and contract changes. Default target: one meaningful behaviour, 1-4 implementation files, one reviewable diff. A larger model adapter may need several sub-tickets. The integrator owns shared files and approves any required seam change before dependent work begins.

## T01 - Reproducible environment and CI gate
Owner: Machine A / Sol high. Depends: T00.
Paths: pyproject.toml, dependency lock, scripts/check.py, .github/workflows/contracts.yml, docs/START_HERE.md.
Seam: `python scripts/check.py` remains the portable baseline; add a locked development environment and the agreed lint/type commands.
Acceptance: clean Python 3.12 installation passes the 42 tests; pytest discovers the same suite; generated schema diff is empty; intentional schema drift fails CI. Run Ruff/mypy and fix actual errors before enabling their gates. Pin supported dependency versions from the resolver, not guessed lock hashes. Do not add GPU packages here.
Verify: `python scripts/check.py`; `python -m pytest -q`; `python scripts/export_schemas.py`; `git diff --exit-code -- schemas`.

## T02 - Publish HTTP transport contracts and fixture examples
Owner: A / Sol high. Depends: T01.
Paths: src/satquery/api/contracts.py, src/satquery/api/app.py, tests/test_api_contracts.py, schemas/http/, apps/web/src/generated/ (generation only).
Seams: `create_app(settings: AppSettings) -> FastAPI`; typed RunRequest/RunSnapshot/ErrorEnvelope/AssetUploadReceipt; routes listed in ARCHITECTURE.md.
Acceptance: a valid run request round-trips; blank query returns 422; unknown field returns 422; unsupported schema version rejected; error response never contains a stack/path/key. Generate TypeScript from published OpenAPI; no independently handwritten duplicate records. Include examples for success, partial and failed states.
Verify: `python -m pytest tests/test_api_contracts.py -q`; generation drift check.

## T03 - Durable run store and idempotency
Owner: A / Sol high. Depends: T02.
Paths: src/satquery/jobs/store.py, src/satquery/jobs/service.py, src/satquery/storage/migrations/, tests/test_jobs.py.
Seams: `submit_run(owner_id: str, key: str, request: RunRequest) -> RunSnapshot`; `claim_next(worker_id: str) -> JobLease | None`.
Acceptance: same owner/key/body gives the same run ID; changed body returns conflict; two simultaneous worker claims cannot both acquire a job; expired lease recoverable; succeeded cannot transition to running; restart preserves state; cancel request remains visible.
Verify: `python -m pytest tests/test_jobs.py -q`. Include a concurrent test using separate database connections.

## T04 - Safe ingest and metadata
Owner: authorised GIS lane / Sol or tested Go model high. Depends: T02.
Paths: src/satquery/ingest/reader.py, src/satquery/ingest/policy.py, tests/test_ingest.py, tests/fixtures/rasters/.
Seam: `inspect_upload(upload_id: str, policy: IngestPolicy) -> AssetRecord` in a restricted worker.
Acceptance: tiny valid TIFF succeeds; malformed TIFF fails safely; PNG without trusted benchmark manifest rejected; filename traversal never controls storage path; unsupported driver/VRT rejected; excessive dimensions/bands/time fail before inference; missing CRS preserved as unknown. Confirm affine order conversion with rotated-grid fixture. Raw bytes never enter the language prompt.
Verify: `python -m pytest tests/test_ingest.py -q`; isolated decoder escape/access controls checked in the worker environment.

## T05 - Real optical single-image route
Owner: model lane / Sol high or tested non-Contributor model. Depends: T02,T04.
Paths: src/satquery/specialists/optical.py, model environment manifest, tests/test_optical_adapter.py, evaluation/optical/.
Seam: `OpticalSpecialist` implements Specialist; named image input and text/box outputs.
Acceptance: real VQA and caption sample with checkpoint and trace; SAR rejected; model absence yields MODEL_UNAVAILABLE; resize/box mapping tested. First try the selected TerraScope/GeoChat candidate within the feasibility timebox, not both indefinitely. A fake provider passes UI tests only.
Verify: `python -m pytest tests/test_optical_adapter.py -q`; separately labelled real model smoke command with captured output.

## T06 - Radar and genuine paired extraction
Owner: strongest available model/GIS lane high; A reviews. Depends: T02,T04.
Paths: src/satquery/specialists/fusion.py, src/satquery/specialists/sar.py, tests/test_fusion_adapter.py, evaluation/fusion/.
Seam: named optical/SAR slots; real compatible encoder/VLM + head behind Specialist.
Acceptance: missing radar rejected for paired request; unsupported processing/polarisation rejected; optical-only, SAR-only and paired results logged; data actually reaches both paths. Support documented single-SAR questions. Grounded region claims require spatial predictions; class labels do not become masks. Co-registration checked beyond equal dimensions.
Verify: `python -m pytest tests/test_fusion_adapter.py -q`; real paired smoke and modality ablation artifact. This is a critical-path task.

## T07 - Temporal route and CDVQA harness
Owner: model lane / Sol high. Depends: T02,T04.
Paths: src/satquery/specialists/temporal.py, src/satquery/evaluation/cdvqa.py, tests/test_temporal_adapter.py.
Seam: named before/after inputs; named before_mask/after_mask/change_text as actually supported; Specialist protocol.
Acceptance: reversed dates fail; outputs preserve image association; full CDVQA data/evaluator acquisition verified; no train/test leakage; change caption alone is not silently used as a CDVQA score. No area calculation when masks/georeferencing are unavailable.
Verify: `python -m pytest tests/test_temporal_adapter.py -q`; real temporal smoke and a documented evaluator subset run.

## T08 - Required visual adaptation
Owner: GPU lane with Sol high guidance. Depends: chosen working T06 backbone and data access.
Paths: training/data_manifest.py, training/train_head.py, training/configs/, tests/test_training_manifest.py, evaluation/adaptation/.
Seam: `build_training_manifest(config: TrainingDataConfig) -> TrainingManifest`; reproducible train/evaluate entrypoints.
Acceptance: test/bench rows excluded; same image pairs cannot leak across development splits; visual/fusion/head parameters actually update; no new LoRA; frozen backbone and training configuration recorded; held-out adapted/unadapted and question-only controls reported. Begin with a pipeline subset; scale only after joins/splits pass.
Verify: `python -m pytest tests/test_training_manifest.py -q`; checkpoint, manifest and held-out report. This cannot be replaced with a prompt-only adapter.

## T09 - Field Desk UI, then live integration
Owner: Machine B / Muse high if approved public-safe export. Depends: T02; live flow also T03,T04 and one real specialist.
Paths: apps/web/src/, apps/web/tests/, UI handoff; shared locks only by explicit assignment.
Seams: generated transport types; one API client interface, no fetch scattered across components.
Acceptance: five routes and required states from UI_SPEC.md; valid input -> real job -> finding -> evidence -> export path; wrong input error is actionable; refresh restores run; reduced motion; no dead buttons. Prototype fixtures visibly labelled until connected. Independent QA owns acceptance expectation, not screenshot auto-update.
Verify: `npm run typecheck`; `npm run test`; assigned `npx playwright test` flows after package scripts are established by owner.

## T10 - Controller, registry and atomic evidence
Owner: A / Sol high; Astra reviews boundaries. Depends: T03-T07.
Paths: src/satquery/controller/, src/satquery/evidence/, tests/test_controller.py.
Seam: `execute_plan(plan: PlanRecord, registry: ToolRegistry, store: ArtifactStore) -> RunOutcome`.
Acceptance: unknown tool/version/target refused; named outputs resolve; mock tool prohibited in real mode; timeout never yields success; both modalities required when requested; required checks fail closed; atomic claims point to existing owned artifacts. An unavailable optional action may yield partial, not fabricated, output.
Verify: `python -m pytest tests/test_controller.py -q`; one real vertical slice through the API and GUI.

## T11 - Report export and scientist feedback
Owner: A or authorised bounded worker / Terra high. Depends: T09,T10.
Paths: src/satquery/reports/, src/satquery/api/feedback.py, tests/test_reports.py, apps/web report components.
Seam: `build_report(run_id: str, owner_id: str) -> ArtifactRef`.
Acceptance: claim IDs resolve; original/derived figures labelled; units/dates/tool versions included; export failure visible; another owner gets no access; feedback tied to run/claim/version. PDF + machine-readable manifest produced from the same run snapshot. Sensitive feedback is private by default.
Verify: `python -m pytest tests/test_reports.py -q`; inspect a rendered report and download through the authenticated route.

## T12 - Claim delta feature
Owner: A / Sol high, fresh reviewer. Depends: T10,T11.
Paths: src/satquery/evidence/revisions.py, tests/test_revisions.py, apps/web revision view.
Seam: `revise_run(run_id: str, changes: RevisionRequest) -> RunSnapshot`.
Acceptance: changed old dependency marks descendants stale; unrelated claim survives; fresh result equals full rerun within declared tolerance; renamed file with identical content does not force inference; changed preprocessing/model digest does; partial rerun cannot relabel stale claim supported. UI shows actual changed claims.
Verify: `python -m pytest tests/test_revisions.py -q`; full-vs-selective replay comparison. Optional for early internal gate; never displace R1-R8.

## T13 - Independent integration and scientific tests
Owner: C / Muse high on approved fixtures; Sol reviews scientific expectations. Depends: relevant merged slices.
Paths: tests/integration/, tests/e2e/, evaluation/reliability/, QA handoff only.
Seam: public HTTP/UI and exported artifacts.
Acceptance: successful required flows plus negative controls; temporal net=gains-losses and gross=gains+losses; degree coordinates cannot become hectares; modality ablation; cloud/nodata/registration cases; risk and coverage both reported. No test based only on another model agreeing. Label synthetic/model/public/hidden-data boundaries explicitly.
Verify: focused pytest/Playwright commands recorded per case. Add cases as capabilities merge, not only at project end.

## T14 - Scientist pilot hardening
Owner: A / Sol high, independent review. Depends: T10,T11,T13.
Paths: auth/access boundaries, deployment configuration, security tests, ops/runbook.md.
Seam: authenticated owner-scoped API/artifact store; process isolation and durable worker lease.
Acceptance: cross-user tiles/artifacts/reports blocked; uploads bounded; decoder cannot access unrelated files/network; restart/timeout/cancel clean; backup restore demonstrated; secret/dependency/source scans triaged; no unresolved critical/high findings. External scans only target our authorised test deployment.
Verify: security regressions, restore drill and scanner evidence. Codex Security is optional and requires access/budget confirmation; a scanner pass does not certify production readiness.

## T15 - Release candidate and actual demo
Owner: A with fresh reviewer and human walkthrough. Depends: R1-R8 complete, T13; T14 for scientist distribution.
Paths: release manifest, model cards, installation guide, demo script, known-issues list.
Seam: a versioned release assembled from tested commits and checkpoint hashes.
Acceptance: clean-machine install, actual GPU measurements, all mandatory flows, failed-input example, real export; public-split scores reproducible; no fabricated live run; restricted-data permissions confirmed. Internal demo and scientist pilot have separate gates. Do not label production-ready without the later operational/evaluation evidence.
Verify: release checklist, replayable demo, exact version/tag. Publishing and external delivery require their own task authorisation.
