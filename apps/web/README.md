# SatQuery Field Desk

Independent React/TypeScript/Vite workbench. It imports no landing code or assets.

## Exact demo startup (WSL Ubuntu)

```bash
cd /home/aryan/satquery-core/apps/web
npm run build
npm run preview -- --host 127.0.0.1
```

Open http://localhost:4173/app/projects/proj-delta. Recorded inference is at
http://localhost:4173/app/recorded/run-01. Vite serves `/app/` and its SPA deep links.
Development: `npm run dev -- --host 127.0.0.1`, then
http://localhost:5173/app/projects/proj-delta.

## Supported workflow

1. Default optical before/after examples are selected; Inputs changes them.
2. Choose Change illustration and click Run example.
3. Explicit simulated stages finish with the supplied finding in about 1.1 seconds
   of foreground UI scheduling. This is not model runtime or backend progress.
4. View evidence opens the matching source image and run identity. Escape closes
   it and returns keyboard focus. Export this result opens the exact submitted run.
5. Reset run clears the result. Changing inputs/question cancels pending simulation
   and clears claims. Another submission receives a new local run ID.

The other choices demonstrate partial optical/SAR support, unavailable captioning,
and a simulated tool error. Arbitrary questions are unsupported, never answered by
an unrelated canned result. No live backend request is made. Recorded run is an
explicit separate choice, never a silent fallback or imitation live sequence.

Completed request descriptors are saved in sessionStorage (last 20). Refresh rebuilds
those results from the supplied fixtures. Closing the browser session loses them.
Reset clears the active result, not the saved report history. Refresh during a pending
simulation returns to an empty state rather than resuming fake work or stale claims.
If browser storage is blocked, the visible result works but saved report retrieval
is unavailable and explains that limitation. Uploads and live inference are not connected.

## Verification

```bash
npm run typecheck
npm test
npm run build
# Requires an existing installed Playwright runtime and Chromium; both previews running.
NODE_PATH=/tmp/shot/node_modules \
LD_LIBRARY_PATH=/tmp/shot/syslibs/usr/lib/x86_64-linux-gnu \
npm run test:browser
```

The browser test uses the existing demo laptop installation; it does not install
packages or start/stop servers. `SATQUERY_EVIDENCE_DIR` overrides the default
`/tmp/satquery-demo-verification` screenshot/results directory. On a different machine,
make its installed `playwright` package resolvable and omit the machine-specific library
path when system Chromium dependencies are already installed.

The workbench presentation model is not a backend transport contract. Python shared
contracts and the recorded original JSON/PNG remain unchanged by this UI repair.
