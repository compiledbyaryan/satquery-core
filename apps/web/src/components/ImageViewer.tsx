import { useState } from "react";
import { SafeImage } from "./SafeImage";
import type { AssetView } from "../viewmodel/types";
interface Props { before?: AssetView; after?: AssetView; activeId?: string; claimRegion?: string }
export function ImageViewer({ before, after, claimRegion }: Props): JSX.Element {
  const [mode, setMode] = useState<"before" | "after" | "split">("split");
  const shown = mode === "before" ? [before] : mode === "after" ? [after] : [before, after];
  return <section className="image-canvas" aria-label="Source imagery viewer">
    <header className="canvas-header"><h2>Observation pair</h2><span className="quiet small">Synthetic · pixel space</span></header>
    <div role="group" aria-label="View mode" className="view-toggle">{(["before", "after", "split"] as const).map(m => <button key={m} className="btn" aria-pressed={mode === m} onClick={() => setMode(m)}>{m === "split" ? "Compare" : m === "before" ? "Before" : "After"}</button>)}</div>
    <div className={mode === "split" ? "swipe" : "single-image"}>{shown.map((a, i) => a ? <figure key={a.id}>
      <SafeImage src={a.previewUrl} alt={`${a.slot === "before" ? "Before" : "After"} synthetic preview`} />
      <figcaption><strong>{a.slot === "before" ? "Before" : "After"}</strong><span>{a.acquiredOn} · synthetic date</span></figcaption>
    </figure> : <div className="image-empty" key={i}><p>{mode === "split" ? i === 0 ? "Before input not selected" : "After input not selected" : "Input not selected"}</p><span>Open Inputs to select an example.</span></div>)}</div>
    <footer className="canvas-caption"><span>Illustration only · no map placement, measured area or calibrated confidence.</span>{claimRegion && <span className="selected-region">Evidence selected: {claimRegion}</span>}</footer>
  </section>;
}
