// Presentation-data interface for the Field Desk workbench.
//
// This is a UI view model only. It is NOT an HTTP contract and MUST NOT be
// mistaken for the backend transport records. Live OpenAPI types will land in
// src/generated/** and the typed client in src/api/** (both owned by the
// integrator). The `connectViewModel` seam documents where that swap happens.

export type FixtureKind = "synthetic";
export type RunStatus =
  | "empty"
  | "queued"
  | "validating"
  | "running"
  | "verifying"
  | "succeeded"
  | "partial"
  | "failed"
  | "cancelled"
  | "model_unavailable"
  | "unsupported";

export type EvidenceCategory = "Measured" | "Model interpretation" | "Not established";

export interface AssetView {
  id: string;
  slot: "optical" | "sar" | "before" | "after";
  label: string;
  /** Acquisition date as supplied text, e.g. "2026-03-14". Unknown stays undefined. */
  acquiredOn?: string;
  modality: "optical" | "sar";
  /** Synthetic preview only: an inline SVG data URL. Never a real raster. */
  previewUrl: string;
  widthPx: number;
  heightPx: number;
  /** True only for fixtures that pretend georeferencing; default false. */
  georeferenced: boolean;
  processingStatus: "ready" | "validating" | "rejected";
  limitation: string;
}

export interface RunEventView {
  id: string;
  seq: number;
  stage: "input_check" | "tool_execution" | "evidence_checks" | "result";
  label: string;
  state: "done" | "active" | "pending";
}

export interface ClaimView {
  id: string;
  shortText: string;
  category: EvidenceCategory;
  /** Only set when the fixture actually supplies a support region. */
  regionLabel?: string;
  sourceAssetId: string;
  sourceDate?: string;
  toolLabel: string;
  limitation: string;
  stale: boolean;
}

export interface RunView {
  id: string;
  projectId: string;
  question: string;
  status: RunStatus;
  inputs: AssetView[];
  events: RunEventView[];
  finding: string;
  claims: ClaimView[];
  limitations: string[];
  notice?: string;
  elapsedSecs?: number;
  modeLabel: "UI prototype — synthetic fixtures" | "Recorded run";
}

export interface ProjectSummary {
  id: string;
  name: string;
  updatedLabel: string;
  runs: RunView[];
}

export interface WorkspaceSelection {
  opticalId?: string;
  sarId?: string;
  beforeId?: string;
  afterId?: string;
}

/** Connection point for the future generated client. */
export interface ViewModelSource {
  kind: "fixtures";
  fixtureKind: FixtureKind;
  listProjects(): ProjectSummary[];
  getProject(id: string): ProjectSummary | undefined;
  getRun(id: string): RunView | undefined;
}

// Placeholder reserved for the integrator-owned generated client.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export type ConnectViewModel = (source: ViewModelSource) => ViewModelSource;
export const connectViewModel: ConnectViewModel = (source) => source;
