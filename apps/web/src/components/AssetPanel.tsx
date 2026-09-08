import { SafeImage } from "./SafeImage";
import type { AssetView, WorkspaceSelection } from "../viewmodel/types";
interface Props { assets: AssetView[]; selection: WorkspaceSelection; onChange: (next: WorkspaceSelection) => void }
export function AssetPanel({ assets, selection, onChange }: Props): JSX.Element {
  return <section className="asset-panel" aria-label="Input assets"><h2>Available examples</h2><p className="quiet small">Synthetic previews and dates. Selection changes clear the current result.</p><div className="asset-list">{assets.map(a => {
    const key = `${a.slot}Id` as keyof WorkspaceSelection;
    const selected = selection[key] === a.id;
    return <article key={a.id} className="asset-card" data-selected={selected}>
      <SafeImage src={a.previewUrl} alt={a.label} />
      <div><h3>{a.slot === "sar" ? "SAR illustration" : `Optical · ${a.slot}`}</h3><p className="quiet small">{a.widthPx} × {a.heightPx} px · {a.acquiredOn} (synthetic date)</p><p className="quiet small">{a.limitation}</p>
      <button className="btn" aria-pressed={selected} onClick={() => { const next = { ...selection }; if (selected) delete next[key]; else next[key] = a.id; onChange(next); }}>{selected ? `Selected as ${a.slot}` : `Use as ${a.slot}`}</button></div>
    </article>;
  })}</div></section>;
}
