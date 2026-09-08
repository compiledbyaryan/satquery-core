import { useState } from "react";
import type { ClaimView } from "../viewmodel/types";

function tagClass(category: ClaimView["category"]): string {
  if (category === "Measured") return "tag tag-measured";
  if (category === "Model interpretation") return "tag tag-model";
  return "tag tag-unknown";
}

export function EvidenceDrawer({
  finding,
  claims,
  limitations,
  notice,
  isError,
  onSelectClaim,
  selectedId
}: {
  finding: string;
  claims: ClaimView[];
  limitations: string[];
  notice?: string;
  isError: boolean;
  onSelectClaim: (id?: string) => void;
  selectedId?: string;
}): JSX.Element {
  const [open, setOpen] = useState(true);
  const selected = claims.find((c) => c.id === selectedId);
  return (
    <section className="evidence-col" aria-label="Findings and evidence">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ fontSize: 14, margin: 0 }}>Findings &amp; evidence</h2>
        <button className="btn" type="button" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
          {open ? "Hide" : "Show"}
        </button>
      </div>
      {notice ? (
        <div className={isError ? "notice error" : "notice"} role={isError ? "alert" : "status"} style={{ marginTop: 10 }}>
          {notice}
        </div>
      ) : null}
      {open ? (
        <div style={{ marginTop: 10 }}>
          {finding ? (
            <div className="finding">
              <span className="kicker">Finding (fixture)</span>
              <p>{finding}</p>
            </div>
          ) : (
            <p className="quiet">No finding yet. Ask a question with inputs selected.</p>
          )}
          {claims.map((c) => (
            <button
              key={c.id}
              className="claim"
              type="button"
              aria-pressed={selectedId === c.id}
              onClick={() => onSelectClaim(selectedId === c.id ? undefined : c.id)}
            >
              <span className={tagClass(c.category)}>{c.category}</span>
              {c.stale ? <span className="tag tag-unknown">stale</span> : null}
              <span style={{ display: "block", marginTop: 6 }}>{c.shortText}</span>
            </button>
          ))}
          {selected ? (
            <div className="drawer" role="dialog" aria-label={`Evidence for ${selected.id}`}>
              <h3>Evidence</h3>
              <dl className="small">
                <dt>
                  <strong>Source</strong>
                </dt>
                <dd className="mono">
                  {selected.sourceAssetId} · {selected.sourceDate ?? "date unknown"}
                </dd>
                <dt>
                  <strong>Computation / model</strong>
                </dt>
                <dd>{selected.toolLabel}</dd>
                <dt>
                  <strong>Support region</strong>
                </dt>
                <dd>{selected.regionLabel ?? "Text-only output — no box drawn (never invented)."}</dd>
                <dt>
                  <strong>Limitation</strong>
                </dt>
                <dd>{selected.limitation}</dd>
              </dl>
              <button className="btn" type="button" onClick={() => onSelectClaim(undefined)}>
                Close (Esc)
              </button>
            </div>
          ) : null}
          {limitations.length > 0 ? (
            <div className="card" style={{ marginTop: 10 }}>
              <strong>Limitations</strong>
              <ul className="small" style={{ margin: "6px 0 0", paddingLeft: 18 }}>
                {limitations.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
