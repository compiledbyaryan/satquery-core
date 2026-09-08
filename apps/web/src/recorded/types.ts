// Typed view of the published recorded-run record.
// Field-for-field with docs/handoffs/recorded-run-01/recorded-run.json.
// No invented fields: confidence, regions, and measurements are absent upstream.

export interface RecordedInvocation {
  task: string;
  prompt: string;
  output: string;
  started_at: string;
  finished_at: string;
  preprocessing_seconds: number;
  generation_seconds: number;
  input_token_count: number;
  output_token_count: number;
}

export interface RecordedRun {
  recorded_run_id: string;
  mode: string;
  validation_status: string;
  human_review_note: string;
  source_commit: string;
  attribution: { dataset: string; model: string };
  evidence_pointers: {
    probe_commit: string;
    manifest: string;
    raw_summary: string;
    raw_invocations: string;
    label_audit_location: string;
  };
  execution: {
    device: string;
    torch_cuda_available: boolean;
    started_at: string;
    finished_at: string;
    elapsed_seconds_total: number;
    load_seconds: number;
    generation: { do_sample: boolean; max_new_tokens: number };
  };
  input: {
    dataset: string;
    dataset_revision: string;
    split: string;
    streaming_row_index: number;
    source_image_id: string;
    source_mode: string;
    size_px: [number, number];
    display_file: string;
    sha256: string;
    opaque_name: string;
  };
  model: {
    name: string;
    revision: string;
    model_class: string;
    processor_class: string;
    parameter_count: number;
    dtype: string;
    device: string;
    preprocessing: Record<string, number | boolean>;
  };
  invocations: RecordedInvocation[];
}

export const RECORDED_RUN_URL = `${import.meta.env.BASE_URL}recorded/recorded-run-01/recorded-run.json`;
export const RECORDED_IMAGE_URL = `${import.meta.env.BASE_URL}recorded/recorded-run-01/recorded_sample_01.png`;
export const RECORDED_IMAGE_SHA256 =
  "916c3b694ce2c971b5d103a46a0e0031192531b35f18d83683c3308802cad484";

export function parseRecordedRun(raw: unknown): RecordedRun {
  const r = raw as RecordedRun;
  if (!r || typeof r !== "object") throw new Error("Recorded run is not an object");
  if (r.recorded_run_id !== "recorded-smollm-cpu-20260908-01") throw new Error("Unexpected recorded_run_id");
  if (r.mode !== "recorded") throw new Error("Unexpected mode");
  if (!Array.isArray(r.invocations) || r.invocations.length === 0) throw new Error("Missing invocations");
  if (typeof r.human_review_note !== "string" || r.human_review_note.length === 0) {
    throw new Error("Missing human_review_note");
  }
  return r;
}
