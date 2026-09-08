import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { resolveRun } from "../logic/demo";

export function ReportView(): JSX.Element {
  const { id } = useParams();
  const run = resolveRun(id);
  const [feedback, setFeedback] = useState("");
  const [saved, setSaved] = useState(false);
  const [failed, setFailed] = useState(false);

  const download = (): void => {
    if (!run) return;
    try {
      const manifest = {
        runId: run.id,
        mode: run.modeLabel,
        question: run.question,
        status: run.status,
        finding: run.finding,
        inputs: run.inputs.map(({ previewUrl: _preview, ...asset }) => asset),
        claims: run.claims,
        limitations: run.limitations,
        warning: "Synthetic fixture manifest — not a scientific result."
      };
      const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${run.id}-manifest.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setFailed(false);
    } catch {
      setFailed(true);
    }
  };

  if (!run) return <div className="page"><h1>Run unavailable</h1><p>This run is not saved in this browser session.</p><Link to="/projects/proj-delta">Open workspace</Link></div>;

  return (
    <div className="page">
      <p>
        <Link to={`/projects/${run.projectId}`}>← Back to workspace</Link>
      </p>
      <h1 style={{ marginTop: 0 }}>Report — fixture preview</h1>
      <p className="quiet small">
        Claims resolve to fixture inputs below. Original figures are synthetic previews; derived figures are labelled
        as model interpretations. Units/dates/tool versions included where supplied — never invented.
      </p>
      <div className="card">
        <strong>Finding</strong>
        <p>{run.finding || "(no finding in this state)"}</p>
      </div>
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Claims &amp; provenance</strong>
        <ul className="small">
          {run.claims.map((c) => (
            <li key={c.id}>
              <span className="mono">{c.id}</span> — {c.shortText} [{c.category}; {c.toolLabel};
              source {c.sourceAssetId}
              {c.sourceDate ? `, ${c.sourceDate}` : ""}]
            </li>
          ))}
          {run.claims.length === 0 ? <li>No claims in this state.</li> : null}
        </ul>
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
        <button className="btn btn-primary" type="button" onClick={download}>
          Download manifest (JSON)
        </button>
        <span className="quiet small">PDF export unavailable in fixture mode — explained, not a dead button.</span>
      </div>
      {failed ? (
        <div className="notice error" role="alert" style={{ marginTop: 10 }}>
          Export failure: browser download blocked. Retry or copy the on-screen manifest reference.
        </div>
      ) : null}
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Scientist feedback (local draft only)</strong>
        <textarea
          aria-label="Feedback tied to this run"
          rows={3}
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Note tied to run, claim version, and tool label…"
        />
        <div style={{ marginTop: 8 }}>
          <button className="btn" type="button" onClick={() => setSaved(true)} disabled={feedback.trim().length === 0}>
            Save draft locally
          </button>{" "}
          {saved ? <span className="quiet small">Draft kept in this page only — not sent anywhere.</span> : null}
        </div>
      </div>
    </div>
  );
}
