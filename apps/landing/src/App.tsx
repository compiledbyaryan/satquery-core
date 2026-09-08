import "./style.css";

// Workspace URL: same-origin `/app/` on a combined host, dev workbench port otherwise.
// Never imports workbench code — plain anchor only.
function workspaceHref(): string {
  if (typeof window !== "undefined" && window.location.port === "5174") return "http://localhost:5173/projects/proj-delta";
  return "/app/projects/proj-delta";
}

export function App(): JSX.Element {
  return (
    <main className="hero">
      <div className="card">
        <a className="skip-link" href="#cta" style={{ position: "absolute", left: -9999 }}>
          Skip to workspace link
        </a>
        <span className="eyebrow">SatQuery · Field Desk</span>
        <h1>Ask Earth. Inspect the evidence.</h1>
        <p className="lede">
          An evidence-grounded workbench for investigating satellite observations — every finding links to its
          source, date, tool, and limitation.
        </p>
        <div className="cta-row">
          <a id="cta" className="cta" href={workspaceHref()}>
            Open workspace
          </a>
        </div>
        <p className="fine">
          Decorative cover only — not a scientific image. The workbench runs independently at its direct URL and
          needs none of this page&apos;s code or assets.
        </p>
      </div>
    </main>
  );
}
