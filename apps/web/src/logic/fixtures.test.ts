import { describe, expect, it } from "vitest";
import { fixtureRuns } from "../fixtures/library";
import { isTerminal, mergeEvents, nextStatus } from "./progress";
import type { RunStatus } from "../viewmodel/types";

const ALL_STATUSES: RunStatus[] = [
  "empty",
  "queued",
  "validating",
  "running",
  "verifying",
  "succeeded",
  "partial",
  "failed",
  "cancelled",
  "model_unavailable",
  "unsupported"
];

describe("no success without a supplied success state", () => {
  it("nextStatus yields succeeded only when success was actually supplied", () => {
    for (const current of ALL_STATUSES) {
      for (const proposed of ALL_STATUSES) {
        const next = nextStatus(current, proposed);
        if (next === "succeeded") {
          // Success on screen requires success in the supplied data:
          // either already the current state, or a forward transition into it.
          expect(proposed === "succeeded" || current === "succeeded").toBe(true);
          // A non-success terminal state can never become success.
          if (current !== "succeeded") expect(isTerminal(current)).toBe(false);
        }
      }
    }
  });

  it("terminal states never regress, including into success", () => {
    for (const current of ALL_STATUSES.filter(isTerminal)) {
      for (const proposed of ALL_STATUSES) {
        expect(nextStatus(current, proposed)).toBe(current);
      }
    }
  });

  it("mergeEvents never invents stages or outcomes", () => {
    for (const run of fixtureRuns) {
      const merged = mergeEvents(run.events, run.events);
      expect(merged.map((e) => e.id).sort()).toEqual(run.events.map((e) => e.id).sort());
      // Polling an empty event list must not produce a success-shaped trace.
      const fromEmpty = mergeEvents([], run.events);
      expect(fromEmpty.length).toBe(run.events.length);
    }
    expect(mergeEvents([], [])).toEqual([]);
  });
});

describe("fixture evidence invariants", () => {
  it("every claim resolves to an input asset of the same run", () => {
    for (const run of fixtureRuns) {
      const inputIds = new Set(run.inputs.map((a) => a.id));
      for (const claim of run.claims) {
        expect(inputIds.has(claim.sourceAssetId)).toBe(true);
      }
    }
  });

  it("only succeeded/partial runs carry claims; nothing else claims success", () => {
    for (const run of fixtureRuns) {
      if (run.status === "succeeded" || run.status === "partial") {
        expect(run.claims.length).toBeGreaterThan(0);
        expect(run.finding.length).toBeGreaterThan(0);
      } else {
        expect(run.claims).toEqual([]);
      }
    }
  });

  it("succeeded runs show only completed stages", () => {
    for (const run of fixtureRuns.filter((r) => r.status === "succeeded")) {
      expect(run.events.length).toBeGreaterThan(0);
      for (const e of run.events) expect(e.state).toBe("done");
    }
  });

  it("failure states stay failures with an actionable notice, never a finding", () => {
    for (const run of fixtureRuns.filter(
      (r) => r.status === "failed" || r.status === "model_unavailable" || r.status === "unsupported"
    )) {
      expect(run.finding).toBe("");
      expect(run.notice).toBeDefined();
      expect((run.notice ?? "").length).toBeGreaterThan(0);
    }
  });
});
