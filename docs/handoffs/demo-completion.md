# Final demo integration — 8 September 2026

Base: `7fd98af4c63636bf6ec2c319e38a43e49fbce56c` (PR #7 merged).
Feature branch: `codex/demo-completion`. Scope: independent frontend apps,
focused browser/unit regression tests, startup/design/handoff documentation.
Backend implementation, shared contracts, dependencies, original recorded artifacts,
and unrelated untracked materials were preserved. User confirmed other OpenCode writers
were stopped before source edits or branch changes.

## Reproduced defect and repair

Before editing, actual browser submission on the previous preview switched to the
static `run-running` fixture after 600ms and never transitioned again. The displayed
42 seconds was a fixture field, not measured live execution. No request left the UI.
Deselecting an input also fell back to that input, leaving the viewer misleadingly populated.

The supported change example now progresses through explicitly simulated stages and
reaches its supplied terminal finding in about 1.1 seconds of foreground scheduling.
No timer is labelled measured backend work. Duplicate submission is blocked synchronously.
Reset/input/question changes cancel pending callbacks and clear claims. Submitted runs
receive separate IDs; their question and selected inputs are retained for evidence,
inspection, and JSON export. Missing inputs and unsupported requests terminate immediately
with recovery actions. Paired example yields partial; unavailable and tool-failure examples
stay explicit. No live provider or backend integration was added.

Original recorded inference remains a separately selected, instant static view with
bounded loading/retry, original output, measured timings and human review. It performs no
new inference. JSON downloads compare byte-for-byte with the original record; PNG hash is
unchanged. The 64×64 benchmark is displayed at 64×64 CSS pixels, never enlarged as detail.

## Design

Warm paper workspace, forest rail, restrained lime action, editorial typography, imagery
as the main canvas. Input selection is behind Inputs; the result panel links to matching
source imagery in an inline evidence drawer. Escape returns focus to the evidence trigger.
The independent landing uses one headline, one Open workspace action, and labelled
SVG contour artwork. No new rendering framework, font download, or hosting architecture.
Installed Impeccable and UI UX Pro Max guidance was read. The Impeccable mechanical detector
returned `[]`. A separate read-only finish review found no material blocker, subject to
confirmation of the final desktop spacing correction. Final screenshots include that correction.

## Exact verification

All listed checks exited 0:
- Workbench `npm run typecheck`, `npm test`: 20 tests in four files; `npm run build`.
- Landing `npm run typecheck`, `npm run build`.
- Existing Python environment `/home/aryan/.venvs/satquery-core-312/bin/python scripts/check.py`:
  42 unittest checks and 82 pytest tests plus 5 subtests; 3 existing deprecation warnings.
- Saved Chromium harness `apps/web/e2e/demo.cjs`: 46 browser checks on both built previews.
- `git diff --check`.

The browser checks cover actual submission through terminal finding/evidence, duplicate
blocking, reset during simulation, repeat runs, stale input removal, missing-input errors,
partial/unavailable/failure/unsupported states and recovery, exact-run report download,
refresh persistence, recorded download byte equality, source hash, native image dimensions,
record load failure/retry, landing click-through, refresh and browser back/forward,
keyboard focus, reduced motion, no browser exceptions, and no horizontal overflow at
1440, 1024 and 390 pixels for workspace, landing and recorded view.

The complete journey was also manually exercised through the Codex browser. Its download
event observer timed out; actual downloads were independently confirmed with the saved
Chromium harness, not inferred from button clicks. Screenshots in `demo-completion/`
were opened and visually inspected, including desktop/mobile evidence and recorded output.

## Directories and startup

Repository (WSL): `/home/aryan/satquery-core`
Windows explorer: `\\wsl.localhost\Ubuntu\home\aryan\satquery-core`

In separate WSL Ubuntu terminals:

```bash
cd /home/aryan/satquery-core/apps/web
npm run build
npm run preview -- --host 127.0.0.1
```

```bash
cd /home/aryan/satquery-core/apps/landing
npm run build
npm run preview -- --host 127.0.0.1
```

Both preview processes were left running in persistent terminal sessions. Strict ports
prevent silently moving to another URL. If a port is already serving the preview, use it;
do not start a duplicate. Servers bind locally and require this laptop/WSL to stay running.

Tested Windows-browser URLs:
- Landing: http://localhost:4174/
- Workspace: http://localhost:4173/app/projects/proj-delta
- Recorded: http://localhost:4173/app/recorded/run-01
- Per-submission inspector/report links under `/app/runs/demo-*` and `/app/reports/demo-*`.

Repeat the browser gate using the existing laptop tooling:

```bash
cd /home/aryan/satquery-core
NODE_PATH=/tmp/shot/node_modules \
LD_LIBRARY_PATH=/tmp/shot/syslibs/usr/lib/x86_64-linux-gnu \
node apps/web/e2e/demo.cjs
```

No new browser dependencies were installed. That runtime is temporary laptop tooling;
other machines need their own installed Playwright/Chromium. Workbench tests/builds use
only the unchanged app dependency lock.

## 90-second rehearsal

- 0–10s: Open landing, click **Open workspace**. Say: “This is the interactive synthetic demo.”
- 10–20s: Show before/after, click **Inputs · 2**, show both selected optical inputs, then close Inputs.
- 20–35s: Keep **Change illustration**, click **Run example** once. Point out the explicit simulated-stage label and terminal finding.
- 35–50s: Click **View evidence →**. Show the matching after preview, source ID, synthetic date and limitation. Press Escape.
- 50–60s: Click **Reset run**. Choose **Optical + SAR · partial** and click **Run example**. Explain missing joint support instead of claiming a full result.
- 60–80s: Click **Recorded run**. Say: “This was real CPU inference recorded earlier, not live analysis.” Show the original tiny image, unedited caption and human-review note. The caption is unreliable, not a supported scientific finding.
- 80–90s: Click **Download run JSON**. Explain that the original output and timings are inspectable and preserved.

Optional failure demonstration: **Caption · unavailable**, **Tool failure · simulated**, or
an arbitrary question all reach an actionable state. **Use change example** restores the
supported selection/question; **Run example** starts a fresh simulation.

## Limits and freeze

Interactive synthetic fixtures and recorded real inference are verified. Live execution,
uploads, arbitrary VQA, temporal/SAR scientific analysis, adaptation/evaluation, calibration,
and PDF reports are not established. This delivery does not certify R1–R8 completion.

Completed runs persist only for this browser session (last 20 descriptors). New browser
sessions cannot retrieve old `demo-*` IDs. Refresh during a pending simulation returns to
empty; it cannot resurrect stale claims. If sessionStorage is unavailable, the visible result
still works but the saved report route clearly reports unavailable. Mobile stacks imagery
and results vertically and requires scrolling. Native-resolution benchmark imagery is
intentionally small. No production hosting or cross-user authorization claim is made.

After this scoped final confirmation, freeze UI features for rehearsal. Do not merge the
feature PR automatically. Preserve the previous known-good commit and existing untracked files.
