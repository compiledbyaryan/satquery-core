# UI specification: Field Desk

Design intent: an exact, calm instrument for investigating Earth observations. Map imagery is the visual centre; controls and evidence are easy to scan. SkyFi references inform density and map prominence, not copied layout/assets or purchasing features.

## Five routes
1. `/` Mission library: recent projects, real run status, New analysis, labelled example datasets. No marketing hero or vanity counters.
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

