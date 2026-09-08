# Internal-demo execution plan — 2026-09-07

## Decision and evidence
Deadline reported by Aryan: college internal pitch tomorrow; 8 minutes presentation/demo,
then 2 minutes Q&A. A later portal submission may allow 3-4 days, but that extension is
user-reported, not a confirmed event rule. Keep required template/slide count when provided.
No new PPT template was accessible in this review environment; do not claim it was read.

Current inspected main: 83f96cea2394d61ee86433e6415aef6b2b30c1d6 (PRs 1-3 merged).
PR4 reviewed at 629d26315804ce7d864bd673c59791945c65a333: no blocking regression in T01
scope; both GitHub checks pass. PR4 is not merged as of this snapshot. Fetch live state
before acting. Annotating the report route enriches inferred FastAPI OpenAPI; unchanged
schemas/ does not prove unchanged HTTP schemas. Record this in the transport handoff.

Current source still includes scripted specialists labelled real, incomplete job/executor
connections, metadata/version issues, empty returned claims and reference-only report
export. No frontend app is present in the inspected tree. CI quality is not completion
of the product. Preserve all R1-R8, including real visual adaptation and paired optical-SAR.
No new LoRA. Never claim production readiness or a guaranteed competition outcome.

## Ownership: two writers, one integration authority
Aryan approves the demo story and merges reviewed PRs. Sol is technical integrator and
backend writer. Muse Contributor is frontend writer in a provisioned sanitized workspace.
This reviewing assistant maintains the decision/recovery documents in its own PR.

| Lane | May change | Must not change |
|---|---|---|
| Sol backend | src/satquery, backend tests, scripts, schemas, Python root config/lock, CI; apps/web/src/api and src/generated for integration | Muse-owned view components/app locks while Muse is editing |
| Muse UI | apps/web except src/api and src/generated; apps/landing; app-local npm/config/locks; docs/handoffs/ui.md | Python, root config/locks, shared schemas, CI, shared docs/status |
| Sol integration window | reviewed frontend patch, API client, necessary UI connection points, CI, documentation | concurrent edits to the same frontend tree |
| Human QA/demo | docs/handoffs/demo.md and approved public asset manifest through integrator | source fixes during rehearsal |
| Reviewer | read-only review; separately assigned docs branch | direct edits to a worker branch |

These scopes explicitly authorize app-local frontend scaffolding which the old T09
prompt did not assign. They do not authorize a root monorepo package manager migration.

Every writer has a distinct working directory and branch, even on one laptop.
Two terminals in the same checkout are NOT independent branches. Worktrees protect
working files but share repository history; they are not Contributor sandboxes.
Contributor uses a sanitized, isolated export with no parent-repo history or credentials.
Scope rules reduce collisions; no process can promise zero integration conflicts.

The integrator provisions the frontend sandbox with an allowlist:
AGENTS.md, README.md (mark historical), docs/PROJECT_CONTEXT.md, ARCHITECTURE.md,
UI_SPEC.md, DEMO_EXECUTION_PLAN.md, RESUME.md, TICKETS.md, prompts/UI_WORKER.md,
reviewed public generated contracts if available, frontend files if present, and
approved synthetic/licensed assets. Exclude .git, .env, tokens, Python environments,
private imagery, reports, research chats, user files and private logs. Record exported
base SHA, file list and hashes. Review asset licences and content; do not assume all
files in a public repository are intended for all third-party services.
The user authorizes this bounded public/synthetic UI assignment. Enforce filesystem/
tool boundaries using the host's supported isolation, not only this prompt. If the
agent host cannot enforce it, use Contributor chat-only generation on approved inputs;
Sol imports generated files. No new service subscription or account is required.

Only Sol updates shared STATUS and contracts during implementation. Workers append
their own handoff. Reserve files before each task, release them at handoff. Freeze
Muse edits during Sol's frontend integration; then return ownership explicitly.

## GitHub-centered workflow
Keep GitHub as the authoritative shared code/history, not a substitute for a runtime.
Use existing working WSL for Python/model execution today. Commit a coherent checkpoint
and push the feature branch after each completed subtask; open draft PR early if useful.
Never claim an unpushed local change is visible to remote reviewers.
Use main only for reviewed integration. No force pushes or direct main edits.
A second machine gets the same repo + exact branch/SHA + lane handoff, and creates
its own checkout/environment. It does not share a writable folder or .venv.
A cloud dev environment is an optional later migration; do not change execution host
the night before the demo unless the local machine is actually blocked.
Do not upload secrets, private imagery, huge checkpoints, or virtual environments.
Track permitted large artifacts through manifests with location/digest/licence.
Actual model/server secrets remain in the trusted runtime, never in a frontend bundle.

## Delivery budgets (planning limits, not guarantees)
Run UI work in parallel with the backend lane. Stop expanding scope when a real path
is missing. These are task timeboxes, not claims that the complete project is feasible
in a fixed number of hours.

0. 15-30 min: merge reviewed T01 and coordination docs, prepare approved UI workspace,
   choose one permitted real investigation and capture current capability evidence.
1. Backend 30-45 min: FIX-02 truthful modes plus a real-model feasibility probe. UI in
   parallel 60-90 min: running workbench with clearly labelled fixture data.
2. Backend 90-150 min if model probe succeeds: one genuine image -> question -> saved
   output -> HTTP result. Resolve input names/versions, payload persistence, honest
   metadata, bounded execution and error states required by that route. Publish
   canonical OpenAPI and generated client inputs. Separate coherent commits.
3. Integration 45-90 min: import frontend, stop UI writer, wire accepted API client,
   verify actual result/evidence and export. Resume Muse for bounded visual polish.
4. 30-45 min optional landing only after working workspace; CSS/layered imagery first.
   In parallel humans rehearse the story and prepare accurate slides.
5. 45-60 min: actual-laptop QA, record a real backup run, freeze exact demo commit,
   rehearse twice; record direct workspace URL and startup/reset procedure.
Some activities overlap; four to seven hours is an aggressive target for a narrow
demonstration if a real model/data path is already feasible. It is not an estimate
for complete mandatory science or production readiness.

45-minute decision: if no real model execution is established, record the exact blocker
(hardware, licence, download, API access, unsupported input). Do not spend all remaining
time on CSS while assuming inference will work later. If only a previously captured
real result is available, label it Recorded run. If only fixtures exist, label Prototype.
Neither fallback satisfies a mandatory live capability; state that gap to the team.

## Backend next assignment: FIX-02 then one real slice
Start after PR4 review/merge. Inspect rather than assume a model is installed.
FIX-02: scripted optical/SAR/temporal/fusion tools cannot be registered as real.
Without a real configured provider return explicit unavailable; do not merely relabel
a fake path after execution. Add regression tests that fail against the old behavior.
Preserve explicit fixture/mock use for UI tests.
Then establish one approved real optical VQA + caption path consuming actual pixels,
using an available checkpoint/provider and recording exact model/preprocessing.
No new paid calls, huge downloads or model licence acceptance without task authorization.
Use existing authorized resources; otherwise return concrete options.
Synthetic image pixel tests validate plumbing, not remote-sensing accuracy.

Publish: executable app command, actual preview/input method, canonical HTTP routes,
generated OpenAPI, run state semantics, payload retrieval and safe errors. No fabricated
HTTP endpoints in frontend. Local single-user demo must not be advertised as an
authenticated multi-tenant service. Bind unprotected dev services locally.
Before connecting UI, prove API submission reaches real execution and retrieves output.
Correct changed-body idempotency rather than preserving the existing wrong expectation.
Carry ownership, exact asset version identity and output naming through the chosen route.
Do not expand schemas just to avoid fixing the runtime interface.

Remaining recovery repairs are FIX-03 interfaces/versions, FIX-04 real limits/payloads,
FIX-05 identity/durability, FIX-06 ingest, FIX-07 live slice and FIX-08 exports.
Order the smallest portions needed for the demonstrable route; preserve explicit
backlog for incomplete acceptance. Do not redesign shared storage in two sessions.

## Frontend delivery
Follow prompts/UI_WORKER.md and UI_SPEC.md. React/TypeScript Vite apps with separate
locks; no landing imports into workbench. Single owner for both UI apps initially.
Build main workspace first with clearly labelled fixtures and a view-data seam. Sol
owns generated HTTP types/client; the UI does not dictate speculative live API shapes.
Early preview deadline is more useful than dozens of screens. One excellent workspace,
a working evidence drawer, honest progress and accessible before/after interaction beat
many unfinished settings pages. Unavailable actions explain why; no dead buttons.

## Demonstration acceptance ledger
Use equal-weight demo checkpoints ONLY as a communication rubric, not engineering effort.
Score a checkpoint 1 only when linked execution evidence exists; otherwise 0.
Report checkpoint count and percentage on each coordinator update.
1. Locked environment, all test styles, Ruff, mypy and schema CI: evidenced in PR4.
2. Approved real imagery + actual single-image VQA/caption execution: not evidenced.
3. HTTP submission -> real execution -> persisted/retrievable result: not evidenced.
4. Interactive workspace connected to that actual run: not evidenced.
5. Finding -> correct source/evidence/limitation inspection: not evidenced.
6. Real temporal and co-registered optical-SAR demonstration: not evidenced.
7. Actual downloadable report/manifest from the run: not evidenced.
8. Exact demo build rehearsed on the presentation machine with honest backup: not evidenced.
Initial rubric: 1/8 = 12.5%, conditional on merging reviewed PR4 for main integration.
Mandatory scientific requirements remain a separate ledger: no R1-R8 completion is
certified here. Visual adaptation/evaluation is required even though it is not a
standalone checkpoint in the short live-demo rubric. Do not conceal it in a percentage.

## Eight-minute pitch and two-minute Q&A
0:00-0:40 problem: a decision-maker must inspect multiple images and justify conclusions.
0:40-1:20 user/question and mandatory capability map (implemented vs pending explicit).
1:20-4:20 demonstration: prepared inputs -> question -> real stages -> finding ->
evidence drawer -> limitation/refused unsupported claim -> available export.
4:20-5:20 architecture: natural language -> typed plan -> tools -> evidence -> answer.
5:20-6:20 technical evidence: actual modality inputs, one negative control, measured
runtime/hardware and honest limits. Never fabricate accuracy or benchmark comparison.
6:20-7:20 differentiator and future: inspectable evidence now if implemented; selective
claim invalidation/replay later; multisensor/adaptation completion has priority over RL.
7:20-8:00 close: exactly what works today, why it matters and next concrete milestone.
Q&A budget 8:00-10:00. Do not consume it with a video.
Keep the required slide template and headings; place these content beats within it.
One main message per slide, readable labels, actual screenshots and one compact system
diagram. No invented judge rubric, competitor score or claimed guaranteed selection.

Optional opening: "Two satellite images can suggest a change. The harder question is:
what changed, what supports that answer, and what should we refuse to conclude?"
Use only if it matches the selected working investigation.
Demo line after an evidence click: "This is the source behind this finding. Here is
the observation; here is the limitation." Speak while the view makes it visible.

Future differentiator: an evidence dependency view where replacing an input marks
affected claims stale, then reruns them. First version can show existing provenance;
automatic invalidation/replay stays labelled planned until implemented and tested.
No claim this is globally novel or that deterministic schemas prove scientific truth.

## Failure rehearsal and scope freeze
Test startup from documented commands, refreshed nested URL, second question, wrong
input, missing provider, timeout/disconnect, source selection and actual file download.
Use permitted local imagery/previews and local fonts. Cache a recorded real output only
with visible run time/identity. No fake waiting sequence to pass replay off as live.
Record 60-90 seconds from a working exact build as an optional backup, not a required
extra pitch segment. If live fails, say "Here is the recorded run from this build."
Freeze features at least 60 minutes before rehearsal/pitch; only demonstrated blockers
may change. Re-run the affected flow and retain the prior known-working version.
Keep the direct workspace bookmark; landing failure must cost zero backend recovery.
Do not promise bug-free or production-ready; aim for a verified internal demo.
