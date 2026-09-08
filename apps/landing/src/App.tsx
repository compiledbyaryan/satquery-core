import "./style.css";

// Workspace URL: same-origin `/app/` on a combined host, dev workbench port otherwise.
// Never imports workbench code — plain anchor only.
// Workbench is served two ways, both verified:
//   dev:      workbench `vite dev` on :5173, no base -> /projects/proj-delta
//   preview:  workbench `vite preview` on :4173 WITH base /app/ -> /app/projects/proj-delta
// (apps/web vite.config.ts base "/app/", router basename detects the /app prefix.)
// A same-origin href keeps landing->workspace working in every served context:
// dev landing (:5174) links to dev workbench (:5173); any same-origin host
// (preview :4174, or combined / + /app/) links to the /app/ workspace path.
function workspaceHref(): string {
  if (typeof window !== "undefined" && window.location.port === "5174") return "http://localhost:5173/projects/proj-delta";
  if (typeof window !== "undefined" && window.location.port === "4174") return "http://localhost:4173/app/projects/proj-delta";
  return "/app/projects/proj-delta";
}

export function App(): JSX.Element {
  return (
    <div className="page">
      <a className="skip-link" href="#cta">
        Skip to workspace link
      </a>
      <header className="site-header">
        <span className="brand">
          <svg className="brand-mark" width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">
            <rect width="32" height="32" rx="7" fill="#12221F" />
            <circle cx="16" cy="14" r="7" fill="none" stroke="#C7DF5A" strokeWidth="2.5" />
            <path d="M10 24l3-3m7 3l-3-3" stroke="#F5F4EF" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <span className="brand-name">SatQuery</span>
          <span className="brand-sub">Field Desk</span>
        </span>
        <span className="status-pill">Internal preview</span>
      </header>
      <main className="hero">
        <div className="hero-copy">
          <span className="eyebrow">SatQuery · Field Desk</span>
          <h1>Ask Earth. Inspect the evidence.</h1>
          <p className="lede">
            A workbench in progress for asking questions about satellite observations and tracing
            each finding to its source, date, tool, and limitation.
          </p>
          <div className="cta-row">
            <a id="cta" className="cta" href={workspaceHref()}>
              Open workspace
            </a>
          </div>
          <p className="meta">
            Direct workbench route: <code>/app/projects/proj-delta</code> · Currently shows
            labelled synthetic fixtures.
          </p>
        </div>
        <figure className="hero-visual">
          <svg viewBox="0 0 480 360" aria-hidden="true" focusable="false">
            <defs>
              <radialGradient id="glow" cx="35%" cy="30%" r="75%">
                <stop offset="0%" stopColor="#C7DF5A" stopOpacity="0.35" />
                <stop offset="55%" stopColor="#3286A4" stopOpacity="0.18" />
                <stop offset="100%" stopColor="#0E1A17" stopOpacity="0" />
              </radialGradient>
              <linearGradient id="land" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#1E3A34" />
                <stop offset="100%" stopColor="#0E1A17" />
              </linearGradient>
            </defs>
            <rect width="480" height="360" rx="16" fill="url(#land)" />
            <rect width="480" height="360" rx="16" fill="url(#glow)" />
            <g stroke="#F5F4EF" strokeOpacity="0.12" strokeWidth="1">
              <path d="M0 72H480M0 144H480M0 216H480M0 288H480M96 0V360M192 0V360M288 0V360M384 0V360" />
            </g>
            <g fill="none" stroke="#C7DF5A" strokeOpacity="0.8" strokeWidth="2">
              <ellipse cx="240" cy="170" rx="150" ry="86" strokeDasharray="6 8" />
            </g>
            <g fill="none" stroke="#F5F4EF" strokeOpacity="0.5" strokeWidth="1.5">
              <ellipse cx="240" cy="170" rx="104" ry="58" />
            </g>
            <circle cx="240" cy="170" r="52" fill="none" stroke="#F5F4EF" strokeOpacity="0.7" strokeWidth="2" />
            <circle cx="240" cy="170" r="6" fill="#C7DF5A" />
            <g fontFamily="monospace" fontSize="11" fill="#F5F4EF" fillOpacity="0.75">
              <text x="316" y="120">AOI · 2026-09</text>
              <text x="96" y="262">OPT / SAR</text>
            </g>
            <g stroke="#B257C7" strokeWidth="2" fill="none">
              <rect x="286" y="196" width="64" height="44" rx="4" strokeDasharray="5 4" />
            </g>
            <circle cx="130" cy="110" r="3" fill="#3286A4" />
            <circle cx="362" cy="256" r="3" fill="#C7DF5A" />
          </svg>
          <figcaption>Decorative cover only — not a scientific image.</figcaption>
        </figure>
      </main>
      <footer className="site-footer">
        <p>
          The workbench runs independently at its direct URL and needs none of this page&apos;s
          code or assets. No new downloads, 3D, or motion required to open it.
        </p>
      </footer>
    </div>
  );
}
