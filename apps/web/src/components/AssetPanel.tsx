import { useState } from "react";
import { SafeImage } from "./SafeImage";
import type { AssetView, WorkspaceSelection } from "../viewmodel/types";

interface Props {
  assets: AssetView[];
  selection: WorkspaceSelection;
  onChange: (next: WorkspaceSelection) => void;
}

export function AssetPanel({ assets, selection, onChange }: Props): JSX.Element {
  const [open, setOpen] = useState(true);
  const toggle = (slot: keyof WorkspaceSelection, id: string): void => {
    onChange({ ...selection, [slot]: selection[slot] === id ? undefined : id });
  };
  return (
    <section className="asset-panel" aria-label="Input assets">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ fontSize: 14, margin: 0 }}>Inputs</h2>
        <button className="btn" type="button" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
          {open ? "Collapse" : "Expand"}
        </button>
      </div>
      {open ? (
        <div style={{ marginTop: 10 }}>
          {assets.map((a) => {
            const key = a.slot === "sar" ? "sarId" : a.slot === "before" ? "beforeId" : a.slot === "after" ? "afterId" : "opticalId";
            const pressed = selection[key as keyof WorkspaceSelection] === a.id;
            return (
              <div key={a.id} className="asset-card" data-selected={pressed}>
                <SafeImage src={a.previewUrl} alt={`${a.label} (synthetic preview)`} />
                <p>
                  <strong>{a.label}</strong>
                </p>
                <p className="quiet small">
                  {a.modality.toUpperCase()} · {a.widthPx}×{a.heightPx} px ·{" "}
                  {a.acquiredOn ? `acquired ${a.acquiredOn}` : "date unknown"} · not georeferenced
                </p>
                <p className="quiet small">Limitation: {a.limitation}</p>
                <button
                  className="btn"
                  type="button"
                  aria-pressed={pressed}
                  onClick={() => toggle(key as keyof WorkspaceSelection, a.id)}
                >
                  {pressed ? `Selected as ${a.slot}` : `Use as ${a.slot}`}
                </button>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="quiet small">Asset panel collapsed to protect map width.</p>
      )}
    </section>
  );
}
