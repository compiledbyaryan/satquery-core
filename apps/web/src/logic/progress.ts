import type { RunEventView, RunStatus } from "../viewmodel/types";

const TERMINAL: ReadonlySet<RunStatus> = new Set([
  "succeeded",
  "partial",
  "failed",
  "cancelled",
  "model_unavailable",
  "unsupported"
]);

export function isTerminal(status: RunStatus): boolean {
  return TERMINAL.has(status);
}

/** Merge polled events: stable IDs, ordered by seq, duplicates tolerated,
 *  terminal run state never regresses. Presentation logic only. */
export function mergeEvents(current: RunEventView[], incoming: RunEventView[]): RunEventView[] {
  const byId = new Map<string, RunEventView>();
  for (const e of current) byId.set(e.id, e);
  for (const e of incoming) {
    const prev = byId.get(e.id);
    if (!prev || e.seq >= prev.seq) byId.set(e.id, e);
  }
  return [...byId.values()].sort((a, b) => a.seq - b.seq);
}

/** Next status must not move a terminal run backwards. */
export function nextStatus(current: RunStatus, proposed: RunStatus): RunStatus {
  if (isTerminal(current)) return current;
  return proposed;
}
