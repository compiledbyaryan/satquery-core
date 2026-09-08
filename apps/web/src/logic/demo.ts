import { fixtureRuns } from "../fixtures/library";
import type { RunView, WorkspaceSelection } from "../viewmodel/types";

export const demoAssets = fixtureRuns.find(r => r.id === "run-success")!.inputs;
export const defaultSelection: WorkspaceSelection = { beforeId: "asset-opt-before", afterId: "asset-opt-after" };
export const demoQuestions = [
  "What changed between the two images near the river corridor?",
  "Compare the optical pair with SAR support.",
  "Describe the land cover in the before image.",
  "Demonstrate a tool failure."
];
export function selectedAssets(selection: WorkspaceSelection) {
  return demoAssets.filter(a => Object.values(selection).includes(a.id));
}
const supplied = (id: string): RunView => fixtureRuns.find(r => r.id === id)!;
export function demoResult(question: string, selection: WorkspaceSelection, id: string): RunView {
  const inputs = selectedAssets(selection);
  const q = question.trim().toLowerCase();
  let template = "run-unsupported";
  let notice: string | undefined;
  if (!inputs.length) {
    template = "run-failed";
    notice = "No inputs selected. Open Inputs and select the before and after examples, then run again.";
  } else if (q === demoQuestions[2].toLowerCase()) {
    template = "run-unavailable";
    notice = "Live captioning is unavailable in this workspace. Open the recorded run, or choose the labelled change example.";
  } else if (q === demoQuestions[3].toLowerCase()) {
    template = "run-failed";
    notice = "Simulated TOOL_ERROR. No result was produced. Choose the change example to recover.";
  } else if (q === demoQuestions[0].toLowerCase() || q === demoQuestions[1].toLowerCase()) {
    if (!inputs.some(a => a.slot === "before") || !inputs.some(a => a.slot === "after")) {
      template = "run-failed";
      notice = "This example needs both before and after inputs. Select the missing input and run again.";
    } else template = q === demoQuestions[1].toLowerCase() ? "run-partial" : "run-success";
  } else {
    notice = "Unsupported question: this demo has no supplied answer for that request. Choose an example question; arbitrary questions are not analysed.";
  }
  if (template === "run-partial" && selection.sarId) {
    notice = "Partial: SAR is selected, but no joint-analysis result is implemented. Only the supplied optical illustration is shown.";
  }
  const base = supplied(template);
  return { ...base, id, question: question.trim(), inputs, elapsedSecs: undefined,
    claims: base.claims.filter(c => inputs.some(a => a.id === c.sourceAssetId)),
    notice: notice ?? base.notice,
    ...(template === "run-partial" && selection.sarId ? {
      finding: "Partial fixture result: an illustrative optical change is supplied. Joint optical–SAR analysis is unavailable.",
      limitations: ["SAR selection does not establish joint analysis or co-registration.", "Support region is illustrative, not a measured footprint."]
    } : {})
  };
}
export function emptyDemo(selection: WorkspaceSelection): RunView {
  return { ...supplied("run-empty"), inputs: selectedAssets(selection) };
}

/** UI-only simulation. Timers sequence supplied illustrations, never backend work. */
export class DemoSession {
  private timers: ReturnType<typeof setTimeout>[] = [];
  private generation = 0;
  private busy = false;
  constructor(private publish: (run: RunView, pending: boolean) => void) {}
  reset(selection: WorkspaceSelection): void {
    this.cancel();
    this.publish(emptyDemo(selection), false);
  }
  cancel(): void {
    this.generation++;
    this.timers.forEach(clearTimeout);
    this.timers = [];
    this.busy = false;
  }
  submit(question: string, selection: WorkspaceSelection, id: string): boolean {
    if (this.busy) return false;
    const result = demoResult(question, selection, id);
    if (!["succeeded", "partial"].includes(result.status)) {
      this.publish(result, false);
      return true;
    }
    this.busy = true;
    const generation = ++this.generation;
    const stage = (status: "queued" | "running" | "verifying"): void => {
      this.publish({ ...result, status, finding: "", claims: [], notice: undefined,
        limitations: ["Simulated transitions through a supplied example. No model or backend is running."],
        events: supplied(status === "queued" ? "run-queued" : "run-running").events.map((e, i) => ({
          ...e, label: ["Input selection", "Example workflow", "Evidence links", "Supplied result"][i],
          state: status === "verifying" ? i < 2 ? "done" : i === 2 ? "active" : "pending" : e.state
        })) }, true);
    };
    stage("queued");
    this.timers = [
      setTimeout(() => { if (generation === this.generation) stage("running"); }, 250),
      setTimeout(() => { if (generation === this.generation) stage("verifying"); }, 650),
      setTimeout(() => {
        if (generation !== this.generation) return;
        this.busy = false;
        this.timers = [];
        this.publish({ ...result, events: result.events.map((e, i) => ({ ...e,
          label: ["Input selection", "Example workflow", "Evidence links", "Supplied result"][i] })) }, false);
      }, 1100)
    ];
    return true;
  }
}

// Store only a validated request descriptor. Results are rebuilt from supplied fixtures,
// never from untrusted stored claims. Terminal runs survive refresh and route navigation.
interface SavedDemo { id: string; question: string; selection: WorkspaceSelection }
function readSaved(): SavedDemo[] {
  try {
    const raw: unknown = JSON.parse(sessionStorage.getItem("satquery-demo-runs") ?? "[]");
    if (!Array.isArray(raw)) return [];
    return raw.filter((x): x is SavedDemo => {
      if (!x || typeof x !== "object" || typeof x.id !== "string" || !x.id.startsWith("demo-") || typeof x.question !== "string") return false;
      if (!x.selection || typeof x.selection !== "object") return false;
      return Object.entries(x.selection).every(([key, value]) =>
        ["beforeId", "afterId", "sarId"].includes(key) && demoAssets.some(a => a.id === value && `${a.slot}Id` === key));
    });
  } catch { return []; }
}
export function saveDemo(run: RunView, selection: WorkspaceSelection): void {
  if (!run.id.startsWith("demo-")) return;
  try {
    const saved = readSaved().filter(r => r.id !== run.id);
    sessionStorage.setItem("satquery-demo-runs", JSON.stringify([...saved, { id: run.id, question: run.question, selection }].slice(-20)));
    sessionStorage.setItem("satquery-last-demo", run.id);
  } catch { /* The visible result remains usable when session storage is unavailable. */ }
}
export function resolveRun(id?: string): RunView | undefined {
  const saved = readSaved().find(r => r.id === id);
  return saved ? demoResult(saved.question, saved.selection, saved.id) : fixtureRuns.find(r => r.id === id);
}
export function lastDemo(): SavedDemo | undefined {
  try { return readSaved().find(r => r.id === sessionStorage.getItem("satquery-last-demo")); } catch { return undefined; }
}
export function forgetLastDemo(): void {
  try { sessionStorage.removeItem("satquery-last-demo"); } catch { /* Optional persistence. */ }
}
