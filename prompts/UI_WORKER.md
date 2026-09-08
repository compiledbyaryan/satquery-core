# UI implementation assignment: internal demo, 2026-09-07

Implement the workbench first, optional landing second. Read the exported AGENTS.md,
PROJECT_CONTEXT.md, ARCHITECTURE.md ADR-006, UI_SPEC.md, and your lane in
DEMO_EXECUTION_PLAN.md. Use the verified base SHA recorded in your export manifest.
You do not need the old research conversations.

This assignment authorizes work only on approved public documentation, frontend code,
synthetic fixtures and reviewed public/licensed visual assets in a separate Contributor
workspace. It does not authorize access to the integrator's home, environment, Git
history, credentials, private data or restricted imagery. The trusted integrator
provisions and verifies the isolated environment and allowlist before launch; a new
directory or instruction alone is not a sandbox. If isolation is unavailable, use
chat-only code/artifact generation for the same public inputs and let the integrator
apply the output. Do not acquire credentials to bypass this boundary.

Allowed:
- apps/web/** except src/generated/** and src/api/** reserved for integration.
- apps/landing/** after the workbench preview and core interactions work.
- App-local package.json, package-lock.json, tsconfig, Vite config and Playwright config.
- docs/handoffs/ui.md.
No root lock/config, Python files, shared schemas, CI, AGENTS or shared STATUS changes.
No application-wide shared packages. Use React + TypeScript with Vite; app-local npm
locks. Check compatible dependencies from official sources; avoid component-library piles.

Build a small view-model interface and labelled fixture source outside src/api.
It is a UI presentation model, not an invented HTTP contract. Render queued/running/
partial/error/success explicitly; keep mock labels visible. Do not send imagined fetch
requests or claim a live server is integrated. Leave generated API/client directories
for Sol; document the data-source connection point. Complete one useful preview early.

Follow the Evidence Atlas design, honest progress and signature evidence interaction
in UI_SPEC. Keep the map central, collapse optional controls into drawers. Optical,
SAR and temporal controls reflect actual inputs; do not manufacture georeferencing,
bounding boxes, confidence percentages, measurements or source provenance.

Implement the acceptance tests listed in UI_SPEC as relevant to your fixture scope.
Report actual commands/screenshots/results, missing checks and mocked paths. Browser
verification must include responsive layout, keyboard, reduced motion, progress
failure behavior and workbench independence. If browser tools are absent, report that
and give a human checklist; do not claim the browser tests passed.

Use installed Impeccable selectively if actually available. Do not spend the sprint
installing skill collections. Produce original styling from the brief. Optional
landing: one strong reveal, immediate CTA, local poster fallback, no dependency from
the workbench. Never delay an actual result just to finish an animation.

At handoff: provide allowed-path patch/files, changed file list, package commands,
screenshots, fixture labels, tested base SHA, limitations and next connection point.
Do not push to main, merge or deploy. Stop editing frontend files when Sol begins the
integration handoff; resume only after ownership is explicitly returned.
