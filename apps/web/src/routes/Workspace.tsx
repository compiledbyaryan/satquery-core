import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { AssetPanel } from "../components/AssetPanel";
import { EvidenceDrawer } from "../components/EvidenceDrawer";
import { ImageViewer } from "../components/ImageViewer";
import { QueryComposer } from "../components/QueryComposer";
import { ProgressStrip } from "../components/chrome";
import { DemoSession, defaultSelection, demoAssets, demoQuestions, demoResult, emptyDemo, forgetLastDemo, lastDemo, saveDemo, selectedAssets } from "../logic/demo";
import type { WorkspaceSelection } from "../viewmodel/types";

export function Workspace(): JSX.Element {
  const { id } = useParams();
  return <WorkspaceSession key={id} empty={id === "proj-empty"} />;
}
function WorkspaceSession({ empty }: { empty: boolean }): JSX.Element {
  const [saved] = useState(() => empty ? undefined : lastDemo());
  const [selection, setSelection] = useState<WorkspaceSelection>(saved?.selection ?? (empty ? {} : defaultSelection));
  const selectionRef = useRef(selection);
  const [question, setQuestion] = useState(saved?.question ?? demoQuestions[0]);
  const [run, setRun] = useState(() => saved ? demoResult(saved.question, saved.selection, saved.id) : emptyDemo(selection));
  const [pending, setPending] = useState(false);
  const [inputsOpen, setInputsOpen] = useState(empty);
  const [selectedClaim, setSelectedClaim] = useState<string>();
  const [session] = useState(() => new DemoSession((next, busy) => {
    setRun(next); setPending(busy);
    if (!busy) saveDemo(next, selectionRef.current);
  }));
  useEffect(() => () => session.cancel(), [session]);
  const reset = (next = selection): void => {
    forgetLastDemo(); session.reset(next); setSelectedClaim(undefined);
  };
  const changeSelection = (next: WorkspaceSelection): void => {
    selectionRef.current = next; setSelection(next); reset(next);
  };
  const changeQuestion = (next: string): void => { setQuestion(next); reset(); };
  const openExample = (): void => {
    changeSelection(defaultSelection); setQuestion(demoQuestions[0]);
  };
  const inputs = selectedAssets(selection);
  const error = ["failed", "model_unavailable", "unsupported"].includes(run.status);
  const claim = run.claims.find(c => c.id === selectedClaim);
  return (
    <div className="workbench">
      <header className="toolbar">
        <div><h1>River corridor</h1><span className="quiet small">Synthetic observation study</span></div>
        <span className="spacer" />
        <button className="btn" onClick={() => setInputsOpen(v => !v)} aria-expanded={inputsOpen}>Inputs · {inputs.length}</button>
        <button className="btn" onClick={() => reset()}>Reset run</button>
        <Link className="btn" to="/recorded/run-01">Recorded run</Link>
      </header>
      {inputsOpen && <AssetPanel assets={demoAssets} selection={selection} onChange={changeSelection} />}
      <div className="workspace">
        <div className="map-col">
          <ImageViewer before={inputs.find(a => a.slot === "before")} after={inputs.find(a => a.slot === "after")} activeId={selectedClaim} claimRegion={claim?.regionLabel} />
          <QueryComposer pending={pending} question={question} onChange={changeQuestion}
            onSubmit={q => { forgetLastDemo(); setSelectedClaim(undefined); session.submit(q, selection, `demo-${crypto.randomUUID()}`); }}
            activeSummary={inputs.length ? inputs.map(a => `${a.slot} · ${a.acquiredOn} (synthetic date)`).join(" / ") : "No inputs selected"} />
        </div>
        <aside className="result-panel">
          <section className="progress-card" aria-label="Investigation progress">
            <div className="result-heading"><h2>Investigation</h2><span className="status-label" data-status={run.status}>{run.status.replace(/_/g, " ")}</span></div>
            <p className="quiet small">Simulated example workflow · no live analysis</p>
            <div className="progress-body" aria-live="polite"><ProgressStrip events={run.events} status={run.status} /></div>
          </section>
          <EvidenceDrawer key={run.id + run.status} finding={run.finding} claims={run.claims} inputs={run.inputs} runId={run.id}
            limitations={run.limitations} notice={run.notice} isError={error} selectedId={selectedClaim} onSelectClaim={setSelectedClaim} />
          {error && <div className="recovery-actions"><button className="btn btn-primary" onClick={openExample}>Use change example</button><Link to="/recorded/run-01">Open recorded run</Link></div>}
          {!pending && run.status !== "empty" && <div className="run-links"><Link to={`/runs/${run.id}`}>Inspect this run</Link><Link to={`/reports/${run.id}`}>Export this result</Link></div>}
        </aside>
      </div>
    </div>
  );
}
