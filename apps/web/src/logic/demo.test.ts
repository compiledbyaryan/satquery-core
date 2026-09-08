import { afterEach, describe, expect, it, vi } from "vitest";
import { DemoSession, defaultSelection, demoQuestions, demoResult, selectedAssets } from "./demo";
import type { RunView } from "../viewmodel/types";

afterEach(() => vi.useRealTimers());
describe("submitted demo journey", () => {
  it("reaches its supplied terminal finding, blocks duplicates and allows another run", () => {
    vi.useFakeTimers();
    let view: RunView | undefined;
    let pending = false;
    const session = new DemoSession((run, busy) => { view = run; pending = busy; });
    expect(session.submit(demoQuestions[0], defaultSelection, "demo-1")).toBe(true);
    expect(pending).toBe(true);
    expect(session.submit(demoQuestions[0], defaultSelection, "duplicate")).toBe(false);
    vi.runAllTimers();
    expect(pending).toBe(false);
    expect(view?.status).toBe("succeeded");
    expect(view?.finding).toBe(demoResult(demoQuestions[0], defaultSelection, "demo-1").finding);
    expect(view?.id).toBe("demo-1");
    expect(view?.claims.length).toBeGreaterThan(0);
    expect(view?.elapsedSecs).toBeUndefined();
    expect(session.submit(demoQuestions[0], defaultSelection, "demo-2")).toBe(true);
    expect(view?.claims).toEqual([]);
    vi.runAllTimers();
    expect(view?.id).toBe("demo-2");
  });
  it("changing inputs or unmounting cancels pending work and cannot restore stale claims", () => {
    vi.useFakeTimers();
    const publish = vi.fn();
    const session = new DemoSession(publish);
    session.submit(demoQuestions[0], defaultSelection, "old");
    session.reset({ beforeId: defaultSelection.beforeId });
    vi.runAllTimers();
    const [run, busy] = publish.mock.calls[publish.mock.calls.length - 1];
    expect(run.status).toBe("empty");
    expect(run.claims).toEqual([]);
    expect(run.inputs.map((a: {id: string}) => a.id)).toEqual(["asset-opt-before"]);
    expect(busy).toBe(false);
    session.submit(demoQuestions[0], defaultSelection, "unmounted");
    session.cancel();
    const count = publish.mock.calls.length;
    vi.runAllTimers();
    expect(publish).toHaveBeenCalledTimes(count);
  });
  it.each([
    [demoQuestions[2], "model_unavailable"], [demoQuestions[3], "failed"],
    ["How many cars are there?", "unsupported"], ["Is there new built-up area in the after image?", "unsupported"]
  ])("%s terminates actionably without running a timer", (question, status) => {
    vi.useFakeTimers();
    const publish = vi.fn();
    new DemoSession(publish).submit(question, defaultSelection, "demo-negative");
    const [run, busy] = publish.mock.calls[0];
    expect(run.status).toBe(status);
    expect(run.notice).toBeTruthy();
    expect(run.claims).toEqual([]);
    expect(busy).toBe(false);
    expect(vi.getTimerCount()).toBe(0);
  });
  it("requires selected optical inputs and binds every evidence source to this run", () => {
    expect(selectedAssets({})).toEqual([]);
    expect(demoResult(demoQuestions[0], {}, "none").status).toBe("failed");
    expect(demoResult(demoQuestions[0], { beforeId: "asset-opt-before" }, "missing").status).toBe("failed");
    for (const question of demoQuestions.slice(0, 2)) {
      const run = demoResult(question, defaultSelection, "evidence");
      for (const claim of run.claims) expect(run.inputs.find(a => a.id === claim.sourceAssetId)?.acquiredOn).toBe(claim.sourceDate);
      expect(run.claims.some(c => c.sourceAssetId === "asset-sar")).toBe(false);
    }
  });
  it("paired example reaches the supplied partial result, without inventing joint analysis", () => {
    vi.useFakeTimers();
    const publish = vi.fn();
    new DemoSession(publish).submit(demoQuestions[1], defaultSelection, "partial");
    vi.runAllTimers();
    expect(publish.mock.calls[publish.mock.calls.length - 1][0].status).toBe("partial");
    expect(publish.mock.calls[publish.mock.calls.length - 1][0].finding).toContain("Partial result");
    const selected = demoResult(demoQuestions[1], { ...defaultSelection, sarId: "asset-sar" }, "paired");
    expect(selected.status).toBe("partial");
    expect(selected.finding).toContain("unavailable");
  });
});
