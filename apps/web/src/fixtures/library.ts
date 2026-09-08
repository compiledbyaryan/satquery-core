// Labelled synthetic fixtures. Every preview is a generated SVG data URL —
// no real raster, no real measurement, no real georeferencing.

import type { AssetView, ProjectSummary, RunView } from "../viewmodel/types";

function svgPreview(background: string, label: string, sub: string): string {
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420">` +
    `<rect width="640" height="420" fill="${background}"/>` +
    Array.from({ length: 9 })
      .map((_, i) => `<rect x="${40 + i * 62}" y="40" width="2" height="340" fill="#ffffff" opacity="0.12"/>`)
      .join("") +
    Array.from({ length: 7 })
      .map((_, i) => `<rect x="30" y="${50 + i * 52}" width="580" height="2" fill="#ffffff" opacity="0.10"/>`)
      .join("") +
    `<rect x="120" y="120" width="180" height="120" fill="#ffffff" opacity="0.28"/>` +
    `<rect x="330" y="90" width="150" height="190" fill="#15251F" opacity="0.35"/>` +
    `<path d="M60 330 Q200 250 330 300 T590 260" stroke="#C7DF5A" stroke-width="5" fill="none" opacity="0.9"/>` +
    (label.startsWith("AFTER") ? `<rect x="350" y="185" width="85" height="60" fill="#E5E6B2"/>` : "") +
    `<text x="36" y="392" font-family="monospace" font-size="22" fill="#F5F4EF">${label}</text>` +
    `<text x="36" y="60" font-family="monospace" font-size="15" fill="#F5F4EF" opacity="0.85">${sub}</text>` +
    `</svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

const opticalBefore: AssetView = {
  id: "asset-opt-before",
  slot: "before",
  label: "Optical · before (synthetic preview)",
  acquiredOn: "2026-02-10",
  modality: "optical",
  previewUrl: svgPreview("#3E5C4B", "BEFORE · synthetic", "640x420 px · not georeferenced"),
  widthPx: 640,
  heightPx: 420,
  georeferenced: false,
  processingStatus: "ready",
  limitation: "Synthetic preview. No CRS, no registration, no area units."
};

const opticalAfter: AssetView = {
  id: "asset-opt-after",
  slot: "after",
  label: "Optical · after (synthetic preview)",
  acquiredOn: "2026-03-14",
  modality: "optical",
  previewUrl: svgPreview("#2E4A5A", "AFTER · synthetic", "640x420 px · not georeferenced"),
  widthPx: 640,
  heightPx: 420,
  georeferenced: false,
  processingStatus: "ready",
  limitation: "Synthetic preview. Before/after alignment is illustrative only."
};

const sarAsset: AssetView = {
  id: "asset-sar",
  slot: "sar",
  label: "SAR · single look (synthetic preview)",
  acquiredOn: "2026-03-13",
  modality: "sar",
  previewUrl: svgPreview("#4A4A52", "SAR · synthetic", "640x420 px · not georeferenced"),
  widthPx: 640,
  heightPx: 420,
  georeferenced: false,
  processingStatus: "ready",
  limitation: "Synthetic preview. Polarisation/processing not established."
};

function baseRun(over: Partial<RunView>): RunView {
  return {
    id: "run-base",
    projectId: "proj-delta",
    question: "What changed between the two images near the river corridor?",
    status: "empty",
    inputs: [opticalBefore, opticalAfter],
    events: [],
    finding: "",
    claims: [],
    limitations: [],
    modeLabel: "UI prototype — synthetic fixtures",
    ...over
  };
}

export const fixtureRuns: RunView[] = [
  baseRun({
    id: "run-empty",
    status: "empty",
    finding: "",
    limitations: ["No run submitted yet. Select inputs and ask a question."]
  }),
  baseRun({
    id: "run-queued",
    status: "queued",
    question: "Is there new built-up area in the after image?",
    events: [
      { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "active" },
      { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "pending" },
      { id: "e3", seq: 3, stage: "evidence_checks", label: "Evidence checks", state: "pending" },
      { id: "e4", seq: 4, stage: "result", label: "Result", state: "pending" }
    ],
    finding: "Queued behind one job. No finding yet.",
    limitations: ["Position in queue is illustrative in fixture mode."]
  }),
  baseRun({
    id: "run-running",
    status: "running",
    question: "Is there new built-up area in the after image?",
    events: [
      { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" },
      { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "active" },
      { id: "e3", seq: 3, stage: "evidence_checks", label: "Evidence checks", state: "pending" },
      { id: "e4", seq: 4, stage: "result", label: "Result", state: "pending" }
    ],
    finding: "Tool execution in progress. Partial tiles visible; no conclusion yet.",
    limitations: ["Elapsed time is wall time, not percent complete."],
    elapsedSecs: 42
  }),
  baseRun({
    id: "run-partial",
    status: "partial",
    question: "What changed between the two images near the river corridor?",
    events: [
      { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" },
      { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "done" },
      { id: "e3", seq: 3, stage: "evidence_checks", label: "Evidence checks", state: "done" },
      { id: "e4", seq: 4, stage: "result", label: "Result", state: "done" }
    ],
    finding: "Partial result: after-image region readable; SAR input missing so joint analysis was skipped.",
    claims: [
      {
        id: "claim-p1",
        shortText: "After image shows a bright rectangular patch absent before (illustrative).",
        category: "Model interpretation",
        regionLabel: "Illustrative rectangle, after image only",
        sourceAssetId: "asset-opt-after",
        sourceDate: "2026-03-14",
        toolLabel: "fixture-optical-v0 (synthetic)",
        limitation: "No calibrated confidence. No ground truth attached.",
        stale: false
      }
    ],
    limitations: [
      "SAR slot unfilled — paired analysis unavailable, not inferred.",
      "Support region is illustrative, not a measured footprint."
    ],
    notice: "Partial: SAR input missing."
  }),
  baseRun({
    id: "run-success",
    projectId: "proj-delta",
    status: "succeeded",
    question: "What changed between the two images near the river corridor?",
    inputs: [opticalBefore, opticalAfter, sarAsset],
    events: [
      { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" },
      { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "done" },
      { id: "e3", seq: 3, stage: "evidence_checks", label: "Evidence checks", state: "done" },
      { id: "e4", seq: 4, stage: "result", label: "Result", state: "done" }
    ],
    finding: "Fixture finding: the after preview differs from before along the corridor line. Treat as illustration only.",
    claims: [
      {
        id: "claim-s1",
        shortText: "After preview contains a bright patch not present before (illustrative).",
        category: "Model interpretation",
        regionLabel: "Illustrative patch, after image",
        sourceAssetId: "asset-opt-after",
        sourceDate: "2026-03-14",
        toolLabel: "fixture-temporal-v0 (synthetic)",
        limitation: "Illustrative region. No measured area; pixel counts are not hectares.",
        stale: false
      },
      {
        id: "claim-s2",
        shortText: "SAR preview retained as an input; no joint measurement claimed.",
        category: "Not established",
        sourceAssetId: "asset-sar",
        sourceDate: "2026-03-13",
        toolLabel: "fixture-sar-v0 (synthetic)",
        limitation: "Co-registration not established in fixtures.",
        stale: false
      }
    ],
    limitations: [
      "All numbers/regions synthetic. No confidence percentages.",
      "Image viewer uses pixel coordinates; nothing is map-placed."
    ]
  }),
  baseRun({
    id: "run-failed",
    status: "failed",
    question: "Is there new built-up area in the after image?",
    events: [
      { id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" },
      { id: "e2", seq: 2, stage: "tool_execution", label: "Tool execution", state: "done" },
      { id: "e3", seq: 3, stage: "evidence_checks", label: "Evidence checks", state: "done" },
      { id: "e4", seq: 4, stage: "result", label: "Result", state: "done" }
    ],
    finding: "",
    limitations: ["Tool execution failed on synthetic input."],
    notice: "Failed: fixture tool returned TOOL_ERROR (synthetic). Retry with the same inputs."
  }),
  baseRun({
    id: "run-unavailable",
    status: "model_unavailable",
    question: "Describe the land cover in the before image.",
    events: [{ id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" }],
    finding: "",
    limitations: ["No real provider configured in fixture mode."],
    notice: "Model unavailable: real optical specialist not configured. Fixtures cannot substitute."
  }),
  baseRun({
    id: "run-unsupported",
    status: "unsupported",
    question: "Who owns this parcel and what is it worth?",
    events: [{ id: "e1", seq: 1, stage: "input_check", label: "Input check", state: "done" }],
    finding: "",
    limitations: ["Ownership/valuation is out of scope and refused without evidence."],
    notice: "Unsupported request: ownership and valuation are refused in this workbench."
  })
];

export const fixtureProjects: ProjectSummary[] = [
  {
    id: "proj-delta",
    name: "River corridor — illustration",
    updatedLabel: "Updated 2026-09-07 (fixtures)",
    runs: fixtureRuns
  },
  {
    id: "proj-empty",
    name: "New investigation (empty)",
    updatedLabel: "No runs yet",
    runs: []
  }
];

export const exampleQuestions: string[] = [
  "What changed between the two images near the river corridor?",
  "Is there new built-up area in the after image?",
  "Describe the land cover in the before image."
];
