# UI specification: Field Desk

Design intent: an exact, calm instrument for investigating Earth observations. Map imagery is the visual centre; controls and evidence are easy to scan. SkyFi references inform density and map prominence, not copied layout/assets or purchasing features.

## Two independent applications (ADR-006; user decision, 2026-09-07)
The optional cinematic landing lives in `apps/landing/`; the workbench lives in
`apps/web/`. Each has its own build, package manifest and lock. Do not introduce a
root workspace or shared runtime package for the internal demo. Workbench code must
not import landing code, Three.js, GSAP or landing video assets. Share documented
brand values, not a mandatory runtime dependency. Keep the workbench independently
startable and bookmark its direct URL. On a combined host the intended mounts are
`/` for landing and `/app/` for the workbench; configure router/build bases and
SPA deep-link fallback explicitly. Separate dev ports are acceptable. These are
frontend locations, not new API endpoints.

Build the workbench first, then the landing. The earlier ban on a marketing hero
applies inside the workbench, not to the separate landing application. This resolves
the later user request without replacing the five internal workbench routes.

## Five workbench routes (relative to its configured base)
1. `/` Mission library: recent projects, real run status, New analysis, labelled example datasets. No marketing hero or vanity counters inside the workbench.
2. `/projects/:id` Workspace: assets, query, map and evidence. Primary working screen.
3. `/runs/:id` Run inspector: observable steps, tool versions, parameters, checks and artifacts.
4. `/reports/:id` Report: claims, map figures, limitations, provenance, download and scientist feedback.
5. `/settings` Data/runtime settings: provider readiness, local/private mode, job limits and retention. No secret values shown.
Authentication can add a sixth access screen when the pilot is remotely hosted. Upload, metadata, feedback and layer styling are drawers, not additional navigation pages.

## Desktop workspace
At 1440x900: 56px navigation rail; 260px collapsible asset panel; flexible map of at least 600px when side panels permit; 340px answer/evidence inspector; 52px top toolbar; 64px optional temporal strip. When both sidebars would crush the map, collapse assets first. At 1024px keep one sidebar. At mobile widths offer report inspection and basic controls; full analysis is desktop-first.

Top toolbar: project name, AOI selector, dated input status, view controls and Export. Asset panel: optical/SAR/before/after assignments, acquisition dates, thumbnail, processing status, quality limitations. Query composer is adjacent to the evidence panel and includes context-specific example questions. Do not make users repeat which inputs are selected.

Answer hierarchy: short finding, claim rows, affected regions, evidence status and limitations. Selecting a claim highlights its support region, relevant date(s), source layer(s) and computation. Highlight uncertainty with labelled hatching or outlines, not colour alone. Deterministic figures and model interpretations must be visually distinguishable.

Core map interactions: pan/zoom, fit AOI, layer toggle/opacity, before-after swipe, optical/SAR toggle, click claim-to-region and region-to-evidence. Keep source attribution and north/scale indicators where spatial metadata supports them. Ungeoreferenced benchmark images use an image viewer with pixel coordinates, not a fabricated map placement.

## Visual tokens
- Canvas `#F5F4EF`; panel `#FFFFFF`; ink `#15251F`; quiet text `#59675F`; divider `#DCE2D8`.
- Navigation `#12221F`; action accent `#C7DF5A` with dark text; technical link `#176F68`.
- Changed-region outline `#B257C7`; water `#3286A4`; invalid/error `#B53D36`; unresolved `#A36517` plus label.
- Typeface: locally served IBM Plex Sans or system sans; IBM Plex Mono/system mono for timestamps, coordinates and trace values. Confirm font licence when vendoring.
- 4/8px spacing rhythm, 8px component radius, restrained shadows on floating controls, borders for panel separation. No glass everywhere, gradient blobs, decorative stars, excessive pills or placeholder performance counters.

## Motion
Use 140-180ms hover/focus transitions and 180-240ms panel transitions. Prefer opacity/transform; avoid animating large layout dimensions. A new claim may gently highlight its map region once. Respect reduced-motion preferences and support keyboard alternatives to dragging. Model progress comes from observed states and completed tiles; never animate a fake completion percentage or move a progress bar independently of execution.

## Required states
Empty; validating upload; upload rejected; metadata incomplete; queued; running; verification; partial result; success; cancellation; timeout; model unavailable; network disconnect/reconnect; stale claim; unsupported request; export failure. Every action needs a defined response, disabled/loading state and recovery path. Do not render decorative buttons without functionality.

## Acceptance
Keyboard focus visible; controls have names; contrast checked; overlays explain units/source/date; tooltips work without hover; reduced-motion mode checked; no horizontal page overflow at 1440/1280/1024; spinner replaced by factual stage text; refresh preserves run state; cross-user artifact access blocked; user can reach source evidence from a claim in two interactions or fewer. Target browser responsiveness on the actual demo laptop, measured under a representative raster load.

Use Impeccable selectively for critique, audit, polish and simplification. Browser screenshots, Playwright flows and human use decide quality. The PDF design plate is an illustrative layout, not a running application or scientific result.


## Internal-demo visual direction
Concept: Evidence Atlas. One editorial opening line, "Ask Earth. Inspect the evidence."
Use a dramatic but brief imagery composition on the landing, then a calm, precise
workbench. No required scroll sequence or delayed Try SatQuery button. First choice:
CSS image layers and a lightweight optional local video/poster; defer Blender and a
real-time 3D scene until the actual demo works. Decorative generated imagery must not
be confused with scientific source images.

Show only question, active inputs and main finding initially. Move advanced settings,
full trace, model details and export options into labelled drawers. Preserve discovery
with visible tooltips/help and keyboard controls. At smaller widths prioritize the
image and finding over simultaneous panels. Apple-like restraint means clear hierarchy,
spacing and consistent behavior; it does not mean hiding necessary scientific context.

## Investigation progress (actual events, not theatrical completion)
When submitted, show a compact investigation strip rather than a blocking full-screen
animation: input check, tool execution, evidence checks, result. Each stage appears or
changes only when corresponding backend events exist. Unsupported stages are omitted,
not fabricated. Use a gentle pulse/sweep for indeterminate active work; elapsed time is
wall time, not percent complete. Keep source imagery visible and interactive.
Events require stable IDs and ordered sequence handling; repeated/out-of-order polls
must not regress terminal state. Stop animation on completion, failure or cancellation.
Reduced motion uses static stage labels. Announce meaningful changes with a polite
live region without announcing every timer tick. Reconnect resumes server state.
Fixture mode has a persistent "UI prototype — synthetic fixtures" label. Recorded
real results display "Recorded run" and their execution time, never simulated live work.

## Signature interaction: inspect a finding
A selected claim reveals its source image/date, actual support artifact, computation
or model identity, and a specific limitation in one drawer. Highlight only a region
actually provided by the evidence; text-only outputs must not acquire invented boxes.
Use "Measured", "Model interpretation", and "Not established" where evidence supports
those distinctions. These labels are evidence categories, not calibrated probabilities.
No claim of first-of-its-kind novelty is required.

## Frontend acceptance checks for the internal demo
These are required planned tests, not a claim that tests already exist.
- Production build and TypeScript checks for each app independently.
- Workbench build/start succeeds in a clean temporary copy without apps/landing.
- Direct workspace entry, nested-route refresh and browser back/forward work.
- Invalid inputs, unavailable provider, disconnect, retry, partial and failed results
  have actionable UI; none silently become success.
- Repeated submission preserves a single UI submission while pending; actual backend
  idempotency is independently tested by Sol.
- Selecting a claim reveals the matching evidence; unsupported evidence is labelled.
- Before/after slider supports keyboard control; layers retain correct dates/identity.
- Progress follows supplied events, tolerates duplicates and never regresses a terminal
  state. Fixture tests prove presentation behavior, not backend functionality.
- Live smoke: actual request -> retrievable finding -> evidence -> real download.
  Unimplemented controls are disabled with explanation, not decorative dead buttons.
- Playwright checks at 1440, 1024 and 390 widths: no page overflow, named controls,
  visible focus, drawers close with Escape; reduced-motion mode has no continuous motion.
- Missing video/WebGL/network assets do not block Try SatQuery or workbench entry.
- Prefer event/condition assertions over arbitrary sleeps. Small screenshots complement
  behavior tests; do not auto-accept changed baselines or claim tests are unbreakable.
- Measure load/interaction on the actual demo laptop; cap polish to avoid jeopardizing
  working input, result and evidence paths. Target <=3s local usable UI and responsive
  controls under representative imagery; report measured values, not promises.
