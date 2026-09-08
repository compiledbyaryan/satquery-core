import { Link, useParams } from "react-router-dom";
import { ProgressStrip } from "../components/chrome";
import { fixtureRuns } from "../fixtures/library";

export function RunInspector(): JSX.Element {
  const { id } = useParams();
  const run = fixtureRuns.find((r) => r.id === id) ?? fixtureRuns[0];
  return (
    <div className="page">
      <p>
        <Link to={`/projects/${run.projectId}`}>← Back to workspace</Link>
      </p>
      <h1 style={{ marginTop: 0 }}>Run inspector</h1>
      <p className="quiet mono small">
        {run.id} · {run.status} · {run.modeLabel}
      </p>
      <div className="card">
        <strong>Question</strong>
        <p style={{ margin: "6px 0 0" }}>{run.question || "(empty)"}</p>
      </div>
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Steps (observed fixture events)</strong>
        <div style={{ marginTop: 8 }}>
          <ProgressStrip events={run.events} status={run.status} />
        </div>
        <ul className="small">
          <li>Tool versions: fixture-only labels on each claim (e.g. fixture-temporal-v0).</li>
          <li>Parameters: before/after slots from the fixture project; SAR omitted unless selected.</li>
          <li>Checks: evidence checks pass only in the success/partial fixtures; failure fixtures stay failed.</li>
        </ul>
      </div>
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Artifacts (synthetic)</strong>
        <ul className="small">
          {run.inputs.map((a) => (
            <li key={a.id} className="mono">
              {a.id} · {a.modality} · {a.widthPx}×{a.heightPx}px · {a.acquiredOn ?? "date unknown"}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
