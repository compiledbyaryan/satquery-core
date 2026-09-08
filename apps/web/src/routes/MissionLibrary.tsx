import { Link } from "react-router-dom";
import { fixtureProjects } from "../fixtures/library";

export function MissionLibrary(): JSX.Element {
  return (
    <div className="library">
      <h1 style={{ marginTop: 0 }}>Mission library</h1>
      <p className="quiet">
        Recent investigations and labelled example datasets. No marketing hero here — the workbench starts with
        imagery and questions.
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
      <div className="card" style={{ marginTop: 12 }}>
        <strong>Labelled example datasets (synthetic)</strong>
        <ul className="small">
          <li>River corridor before/after pair — temporal illustration, pixel coordinates only.</li>
          <li>Single SAR look — modality toggle illustration, co-registration not established.</li>
        </ul>
      </div>
    </div>
  );
}
