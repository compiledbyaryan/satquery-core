# Handoff: T09 UI polish (no scope expansion)

- Status: needs review (fixture prototype; no live integration claimed)
- Worker: Muse (frontend lane), branch `t09-ui-b-01`
- Base commit: `167f2c7` (origin/main: merge PR6). Ticket docs from PR5 coordination pack
  (base `83f96cea`, ADR-006, UI_SPEC Evidence Atlas, UI_WORKER).
- Scope kept to `apps/web/**` (except reserved `src/api/**`, `src/generated/**`),
  `apps/landing/**`, app-local manifests/locks/configs, this handoff.
  No Python, root config/lock, shared schema, CI, or STATUS edits.

## Polish changes since the first UI handoff

- `components/SafeImage.tsx` (new): failed preview loads degrade to a labelled
  placeholder; the workspace stays usable. Verified by forced-error browser check.
- `components/chrome.tsx`: fixture-strip "Why labelled?" is a real router Link
  (was a `#/settings` hash that resolved nowhere under BrowserRouter).
- `components/ImageViewer.tsx`: removed dead `"sar"` view-mode union member;
  arrow-key nudges clamp to the actual asset dimensions instead of hardcoded 640×420.
- `components/AssetPanel.tsx`: removed invalid `aria-pressed` from a `<div>`
  (selection now a `data-selected` style hook; the toggle button keeps `aria-pressed`).
- `components/QueryComposer.tsx`: example `<select>` starts on a disabled
  "Choose an example…" placeholder instead of silently equating the first example
  with a custom question.
- `components/EvidenceDrawer.tsx` + `app.css`: finding hierarchy (kicker + larger
  finding text, accent rule), tighter claim/limitation spacing, drawer definition
  list margins, `finding` style block.
- `routes/Workspace.tsx`: switching projects resets run/claim/pending state so one
  project's fixture state can never masquerade as another's.
- `app.css`: run selector no longer clips (`max-width 280px`, ellipsis, full-width
  on mobile); before/after split stacks vertically ≤560px so 390px shows one image
  per row instead of two crushed columns.
- `apps/landing/src/App.tsx` + `style.css`: removed the duplicate "Try SatQuery"
  ghost link (same href as the primary CTA — decorative dead action); one immediate
  "Open workspace" CTA remains.

## Regression tests (all in `apps/web`, fixtures/presentation only)

- `src/logic/progress.test.ts` (3 tests): terminal-no-regress, duplicate-tolerant merge.
- `src/logic/fixtures.test.ts` (7 tests, new): success unreachable without a supplied
  success state; terminal states never regress (incl. into success); event merge never
  invents stages; every claim resolves to a same-run input asset; only
  succeeded/partial carry claims+finding; succeeded runs show all-`done` stages;
  failure states stay failures with actionable notice and no finding.

## Browser verification (real, headless Chromium, this session)

- Harness: Playwright 1.63.0 in `/tmp/shot` (outside the repo; user-local browser
  libs fetched via `apt-get download` and extracted to `/tmp/shot/syslibs`, no sudo,
  no repo changes). Served the built `apps/web` (`vite preview :4173`) and
  `apps/landing` (`:4174`).
- Result: **16/16 checks pass**. Screenshots in `/tmp/shot/` (not committed):
  `ws-1440/1024/390`, `ws-evidence`, `ws-focus`, `ws-motion`, `ws-broken`,
  `lib/report/settings-1440`, `landing-1440/390`.
- What passed: no horizontal overflow at 1440/1024/390 on all routes; synthetic
  previews load (640px natural width); claim click opens the evidence dialog with
  source/computation/limitation; Esc dismisses it; Tab order starts at skip-link
  with visible focus; reduced-motion context renders the active stage static
  (`animation none`, dashed border); forced image errors yield 4 labelled
  placeholders with the workspace intact; landing CTA points at `/app/…` with no
  overflow at both widths.
- Inspected screenshots: `ws-1440` (empty state, honest empty copy + limitations),
  `ws-1024` (same layout at 1024, no clipping), `ws-evidence` (success run with
  selected claim, finding hierarchy, evidence drawer), `landing-1440` (single CTA).
  `ws-390`: stacks to one column but the toolbar wraps tall (fixture strip +
  run label + full-width selector + buttons push the imagery down) — usable, not
  broken; recorded as the known mobile trade-off, not claimed ideal.
- Baselines: no screenshot baselines added or auto-accepted; PNGs are evidence only.

## Exact checks, exit results

- `cd apps/web && npm run typecheck` → pass (exit 0)
- `cd apps/web && npm test` → 2 files, 10 tests passed (vitest 2.1.3)
- `cd apps/web && npm run build` → pass (46 modules; `index-BzfhQNfv.js`
  190.32 kB / gzip 60.71 kB; `index-TkfDovA-.css` 6.17 kB / gzip 2.00 kB)
- `cd apps/landing && npm run typecheck` → pass; `npm run build` → pass (31 modules)
- Browser harness: 16/16 pass (see above). No Playwright config added to the repo;
  the harness lives in `/tmp/shot/shoot.js` outside the deliverable.

## Remaining gaps / unrun (distinguished, not claimed)

- Demo-laptop timing (≤3s usable UI, interaction under raster load): UNRUN here.
- Host SPA fallback for `/app/` deep links: documented, still host-configured.
- Manifest download (JSON) works; PDF export explicitly marked unavailable.
- No live backend, no OpenAPI, no generated client — connection point remains
  `connectViewModel` in `viewmodel/types.ts` for Sol's integration window.
- Two repair attempts were not needed (no targeted failure occurred); the one
  failing test during this pass was a wrong test expectation, fixed in the test.

## Interface changes / next dependency

- Public contract changes: none (presentation view-model only; not a transport proposal).
- Next: Sol publishes canonical OpenAPI + generated client into `src/api|generated`,
  wires one real route, verifies live smoke (request → finding → evidence → download).
  UI edits frozen during that window; resume only on explicit return of ownership.
