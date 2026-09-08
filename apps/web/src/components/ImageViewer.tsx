import { useState } from "react";
import { SafeImage } from "./SafeImage";
import type { AssetView } from "../viewmodel/types";

interface Props {
  before?: AssetView;
  after?: AssetView;
  activeId?: string;
  claimRegion?: string;
}

/** Image viewer with pixel coordinates. No map, no CRS, no fabricated placement. */
export function ImageViewer({ before, after, activeId, claimRegion }: Props): JSX.Element {
  const [mode, setMode] = useState<"before" | "after" | "split">("split");
  const [pos, setPos] = useState({ x: 320, y: 210 });
  const shown = mode === "before" ? before : mode === "after" ? after : undefined;
  const bounds = { x: shown?.widthPx ?? 640, y: shown?.heightPx ?? 420 };

  return (
    <div className="card" aria-label="Source imagery viewer">
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <h2 style={{ fontSize: 14, margin: 0 }}>Source imagery (synthetic)</h2>
        <span className="pill">pixel coordinates — not a map</span>
        {claimRegion ? <span className="pill">selected: {claimRegion}</span> : null}
        <span style={{ flex: 1 }} />
        <div role="group" aria-label="View mode">
          {(["before", "after", "split"] as const).map((m) => (
            <button key={m} className="btn" type="button" aria-pressed={mode === m} onClick={() => setMode(m)}>
              {m}
            </button>
          ))}
        </div>
      </div>

      {mode === "split" && before && after ? (
        <div className="swipe" style={{ marginTop: 10 }}>
          <figure>
            <SafeImage src={before.previewUrl} alt="Before synthetic preview" />
            <figcaption className="quiet small mono">
              before · {before.acquiredOn ?? "date unknown"} · {pos.x},{pos.y} px
            </figcaption>
          </figure>
          <figure>
            <SafeImage src={after.previewUrl} alt="After synthetic preview" />
            <figcaption className="quiet small mono">
              after · {after.acquiredOn ?? "date unknown"} · {pos.x},{pos.y} px
            </figcaption>
          </figure>
        </div>
      ) : shown ? (
        <div className="viewer" style={{ marginTop: 10 }}>
          <SafeImage src={shown.previewUrl} alt={`${shown.label}`} />
          <div className="overlay">
            <span className="pill mono">
              x {pos.x}, y {pos.y} px / {shown.widthPx}×{shown.heightPx}
            </span>
            <span className="pill">{shown.acquiredOn ? `acquired ${shown.acquiredOn}` : "date unknown"}</span>
          </div>
        </div>
      ) : (
        <p className="quiet">Select before/after inputs to enable the viewer.</p>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
        <button
          className="btn"
          type="button"
          onClick={() => setPos((p) => ({ x: Math.max(0, p.x - 20), y: p.y }))}
          aria-label="Move inspection point left"
        >
          ←
        </button>
        <button
          className="btn"
          type="button"
          onClick={() => setPos((p) => ({ x: Math.min(bounds.x, p.x + 20), y: p.y }))}
          aria-label="Move inspection point right"
        >
          →
        </button>
        <button
          className="btn"
          type="button"
          onClick={() => setPos((p) => ({ x: p.x, y: Math.max(0, p.y - 20) }))}
          aria-label="Move inspection point up"
        >
          ↑
        </button>
        <button
          className="btn"
          type="button"
          onClick={() => setPos((p) => ({ x: p.x, y: Math.min(bounds.y, p.y + 20) }))}
          aria-label="Move inspection point down"
        >
          ↓
        </button>
        <span className="quiet small">Keyboard-accessible alternative to dragging. {activeId ? `Active: ${activeId}.` : ""}</span>
      </div>
    </div>
  );
}
