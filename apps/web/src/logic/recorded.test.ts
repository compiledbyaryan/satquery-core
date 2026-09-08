import { describe, expect, it } from "vitest";
import original from "../../public/recorded/recorded-run-01/recorded-run.json";
import { parseRecordedRun } from "../recorded/types";
describe("recorded evidence boundary", () => {
  it("preserves original outputs, timings, image identity and review", () => {
    expect(parseRecordedRun(original)).toBe(original);
    expect(parseRecordedRun(original).invocations[0].output).toBe("A blurry image of a building with a person in a dark shirt.");
    expect(parseRecordedRun(original).human_review_note).toBe(original.human_review_note);
  });
  it("rejects malformed nested rendering fields before they reach the page", () => {
    expect(() => parseRecordedRun({ ...original, execution: {} })).toThrow();
    expect(() => parseRecordedRun({ ...original, invocations: [{ output: 42 }] })).toThrow();
    expect(() => parseRecordedRun({ ...original, input: { ...original.input, sha256: "wrong" } })).toThrow();
    expect(() => parseRecordedRun(null)).toThrow();
  });
});
