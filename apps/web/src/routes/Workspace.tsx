import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AssetPanel } from "../components/AssetPanel";
import { EvidenceDrawer } from "../components/EvidenceDrawer";
import { ImageViewer } from "../components/ImageViewer";
import { QueryComposer } from "../components/QueryComposer";
import { ProgressStrip } from "../components/chrome";
import { fixtureProjects, fixtureRuns } from "../fixtures/library";
import type { RunView, WorkspaceSelection } from "../viewmodel/types";

function statusLabel(s: RunView["status"]): string {
  return s.replace(/_/g, " ");
}

export function Workspace(): JSX.Element {
  const { id } = useParams();
  const project = useMemo(
    () => fixtureProjects.find((p) => p.id === id) ?? fixtureProjects[0],
    [id]
  );
  const [runId, setRunId] = useState<string>(project.runs[0]?.id ?? "run-empty");
  const [selection, setSelection] = useState<WorkspaceSelection>({
    beforeId: "asset-opt-before",
    afterId: "asset-opt-after"
  });
  const [pending, setPending] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState<string | undefined>(undefined);

  // Switching projects resets the run/claim view so one project's state
  // can never masquerade as another's.
  useEffect(() => {
    setRunId(project.runs[0]?.id ?? "run-empty");
    setSelectedClaim(undefined);
    setPending(false);
  }, [id, project]);

  const run: RunView = useMemo(
    () => fixtureRuns.find((r) => r.id === runId) ?? fixtureRuns[0],
    [runId]
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent): void => {
      if (e.key === "Escape") setSelectedClaim(undefined);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const before = run.inputs.find((a) => a.id === selection.beforeId) ?? run.inputs.find((a) => a.slot === "before");
  const after = run.inputs.find((a) => a.id === selection.afterId) ?? run.inputs.find((a) => a.slot === "after");
  const claimRegion = run.claims.find((c) => c.id === selectedClaim)?.regionLabel;

  const submit = (question: string): void => {
    if (pending) return; // single UI submission while pending
    setPending(true);
    setSelectedClaim(undefined);
    // Fixture preview: rotate to a labelled state derived from the question.
    const lowered = question.toLowerCase();
    const next = lowered.includes("own") || lowered.includes("worth")
      ? "run-unsupported"
      : lowered.includes("describe") && !lowered.includes("chang")
        ? "run-unavailable"
        : "run-running";
    window.setTimeout(() => {
      setRunId(next);
      setPending(false);
    }, 600);
  };

  const isError = run.status === "failed" || run.status === "model_unavailable" || run.status === "unsupported";

  return (
    <div>
      <div className="toolbar">
        <h1>{project.name}</h1>
        <span className="pill">fixture project</span>
        <span className="spacer" />
        <label className="quiet small" htmlFor="run-select">
          Run
        </label>
        <select id="run-select" value={runId} onChange={(e) => setRunId(e.target.value)}>
          {fixtureRuns.map((r) => (
            <option key={r.id} value={r.id}>
              {r.id} — {statusLabel(r.status)}
            </option>
          ))}
        </select>
        <Link className="btn" to={`/runs/${run.id}`}>
          Inspect run
        </Link>
        <Link className="btn" to={`/reports/${run.id}`}>
          Export
        </Link>
      </div>

      <div className="workspace">
        <AssetPanel assets={run.inputs} selection={selection} onChange={setSelection} />
        <div className="map-col">
          <ImageViewer before={before} after={after} activeId={selectedClaim} claimRegion={claimRegion} />
          <QueryComposer pending={pending} onSubmit={submit} />
          <div className="card" aria-label="Investigation progress">
            <strong>Investigation — actual fixture events only</strong>
            <div style={{ marginTop: 8 }} aria-live="polite">
              <ProgressStrip events={run.events} status={statusLabel(run.status)} />
            </div>
            <p className="quiet small" style={{ marginBottom: 0 }}>
              Stage: <span className="mono">{statusLabel(run.status)}</span>
              {typeof run.elapsedSecs === "number" ? ` · wall time ${run.elapsedSecs}s (not percent)` : ""}
              {" "}· repeated polls never regress a terminal state.
            </p>
          </div>
        </div>
        <EvidenceDrawer
          finding={pending ? "Working on fixture preview…" : run.finding}
          claims={run.claims}
          limitations={run.limitations}
          notice={run.notice}
          isError={isError}
          selectedId={selectedClaim}
          onSelectClaim={setSelectedClaim}
        />
      </div>
    </div>
  );
}
