import { describe, expect, it } from "vitest";
import { isTerminal, mergeEvents, nextStatus } from "./progress";

describe("progress presentation rules", () => {
  it("treats terminal states as terminal", () => {
    expect(isTerminal("succeeded")).toBe(true);
    expect(isTerminal("partial")).toBe(true);
    expect(isTerminal("failed")).toBe(true);
    expect(isTerminal("running")).toBe(false);
    expect(isTerminal("queued")).toBe(false);
  });

  it("never regresses a terminal status on repeated polls", () => {
    expect(nextStatus("succeeded", "running")).toBe("succeeded");
    expect(nextStatus("failed", "queued")).toBe("failed");
    expect(nextStatus("running", "succeeded")).toBe("succeeded");
  });

  it("merges duplicate/out-of-order events by stable id and seq", () => {
    const merged = mergeEvents(
      [{ id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" }],
      [
        { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" },
        { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "active" }
      ]
    );
    expect(merged.map((e) => e.id)).toEqual(["e1", "e2"]);
  });
});
