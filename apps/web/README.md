# SatQuery Field Desk workbench (fixture prototype)

Independent app. No import from `apps/landing`. No live backend calls.

## Run

```bash
cd apps/web
npm install
npm run dev      # http://localhost:5173/ (direct workspace: /projects/proj-delta)
npm run typecheck
npm run build    # emits dist/ with base /app/ for combined host
npm run preview  # serves the /app/ build at http://localhost:4173/app/
npm test         # vitest presentation-logic tests (fixtures only)
```

Combined host intent: landing at `/`, this bundle at `/app/` with SPA fallback to
`/app/index.html`. Router detects the `/app` prefix so deep links and refresh work
in both dev (`/projects/…`) and hosted (`/app/projects/…`) modes.

## Truth boundaries

* `src/viewmodel/` — presentation-data interface only, not an HTTP contract.
* `src/fixtures/` — labelled synthetic SVG previews; pixel coordinates, never map placement.
* `src/api/` and `src/generated/` are reserved for the integrator (generated OpenAPI client).
* Never invents confidence, georeferencing, measurements, or evidence regions.
