# SatQuery landing

Independent React/TypeScript/Vite app. No imports from the workbench.

```bash
cd /home/aryan/satquery-core/apps/landing
npm run typecheck
npm run build
npm run preview -- --host 127.0.0.1
```

Preview: http://localhost:4174/. Its Open workspace link points to
http://localhost:4173/app/projects/proj-delta on this localhost setup.
Development: `npm run dev -- --host 127.0.0.1` at http://localhost:5174/ links to
http://localhost:5173/app/projects/proj-delta. The link retains the current hostname.
On a combined host the link is `/app/projects/proj-delta`; no combined hosting
architecture was added. Deep-link refresh was verified in the separate Vite previews.

The contour artwork is inline SVG, labelled decorative, not satellite imagery.
Entrance motion respects reduced-motion preferences. No external fonts, images,
model downloads, animation frameworks, or service connections are required.
