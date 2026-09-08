import { Link } from "react-router-dom";
import { fixtureProjects } from "../fixtures/library";

export function MissionLibrary(): JSX.Element {
  return (
    <div className="library">
      <h1 style={{ marginTop: 0 }}>Mission library</h1>
      <p className="quiet">
        Choose an interactive synthetic example or inspect the original recorded model output.
      </p>
      <div style={{ marginBottom: 12 }}>
        <Link className="btn btn-primary" to="/projects/proj-empty">
          New analysis
        </Link>
      </div>
      <div className="grid">
        {fixtureProjects.map((p) => (
          <article key={p.id} className="card">
            <h2 style={{ fontSize: 15, margin: "0 0 4px" }}>{p.name}</h2>
            <p className="quiet small" style={{ margin: "0 0 8px" }}>
              {p.updatedLabel} · {p.runs.length} fixture run(s)
            </p>
            <Link className="btn" to={`/projects/${p.id}`}>
              Open workspace
            </Link>
          </article>
        ))}
      </div>
      <div className="card recorded-entry" style={{ marginTop: 12 }}>
        <span className="tag tag-model">Recorded run — not live analysis</span>
        <h2 style={{ fontSize: 15, margin: "8px 0 4px" }}>Recorded model run: SmolVLM on EuroSAT sample 01</h2>
        <p className="quiet small" style={{ margin: "0 0 8px" }}>
          Actual CPU execution (2026-09-08, 203.0s) · verbatim caption + water-QA outputs · human review
          included · not scientifically validated. Separate from synthetic fixtures.
        </p>
        <Link className="btn btn-primary" to="/recorded/run-01">
          Open recorded model run
        </Link>
      </div>
      <div className="card" style={{ marginTop: 12 }}>
        <strong>Labelled example datasets (synthetic)</strong>
        <ul className="small">
          <li>River corridor before/after pair — temporal illustration, pixel coordinates only.</li>
          <li>Single SAR look — selection illustration; joint analysis and co-registration are not established.</li>
        </ul>
      </div>
    </div>
  );
}
