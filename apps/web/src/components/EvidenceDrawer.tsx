import { useEffect, useRef } from "react";
import type { AssetView, ClaimView } from "../viewmodel/types";
import { SafeImage } from "./SafeImage";
interface Props {
  finding: string; claims: ClaimView[]; inputs: AssetView[]; runId: string;
  limitations: string[]; notice?: string; isError: boolean;
  onSelectClaim: (id?: string) => void; selectedId?: string;
}
export function EvidenceDrawer({ finding, claims, inputs, runId, limitations, notice, isError, onSelectClaim, selectedId }: Props): JSX.Element {
  const selected = claims.find(c => c.id === selectedId);
  const source = inputs.find(a => a.id === selected?.sourceAssetId);
  const closeRef = useRef<HTMLButtonElement>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  useEffect(() => {
    if (!selected) return;
    closeRef.current?.focus();
    const escape = (e: KeyboardEvent): void => {
      if (e.key === "Escape") { onSelectClaim(undefined); trigger.current?.focus(); }
    };
    window.addEventListener("keydown", escape);
    return () => window.removeEventListener("keydown", escape);
  }, [selected, onSelectClaim]);
  const close = (): void => { onSelectClaim(undefined); trigger.current?.focus(); };
  return <section className="evidence-col" aria-label="Findings and evidence">
    <h2>Finding &amp; evidence</h2>
    {notice && <div className={isError ? "notice error" : "notice"} role={isError ? "alert" : "status"}>{notice}</div>}
    {finding ? <div className="finding"><p>{finding}</p><span className="quiet small">Supplied synthetic finding</span></div> : <p className="quiet">{isError ? "No supported finding was produced." : "Your result will appear here. Run the selected example to follow a finding back to its source."}</p>}
    {claims.map(c => <button key={c.id} className="claim" type="button" aria-expanded={selectedId === c.id}
      onClick={e => { trigger.current = e.currentTarget; onSelectClaim(selectedId === c.id ? undefined : c.id); }}>
      <span className="tag">{c.category} · fixture</span><span className="claim-text">{c.shortText}</span>
      <span className="claim-cta">{selectedId === c.id ? "Close evidence" : "View evidence →"}</span>
    </button>)}
    {selected && <div className="drawer" role="dialog" aria-label={`Evidence for ${selected.id}`}>
      <div className="result-heading"><h3>Source evidence</h3><button ref={closeRef} className="btn" onClick={close}>Close (Esc)</button></div>
      {source ? <figure className="evidence-source"><SafeImage src={source.previewUrl} alt={`Evidence source: ${source.label}`} /><figcaption>{source.label}</figcaption></figure> : <p role="alert">Matching source unavailable. This claim cannot be inspected.</p>}
      <dl className="small"><dt>Run</dt><dd className="mono">{runId}</dd><dt>Source</dt><dd className="mono">{selected.sourceAssetId} · {selected.sourceDate ?? "date unknown"} (synthetic)</dd>
        <dt>Computation / model</dt><dd>{selected.toolLabel}</dd><dt>Support region</dt><dd>{selected.regionLabel ?? "No spatial region supplied."}</dd><dt>Limitation</dt><dd>{selected.limitation}</dd></dl>
    </div>}
    {!!limitations.length && <details className="limitations" open={isError || undefined}><summary>Limitations</summary><ul className="small">{limitations.map(l => <li key={l}>{l}</li>)}</ul></details>}
  </section>;
}
