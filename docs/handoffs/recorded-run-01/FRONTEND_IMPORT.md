# Recorded-run handoff 01 — frontend import guide (no live backend change)

**Directory:** `docs/handoffs/recorded-run-01/`
- `recorded-run.json` — the versioned record. Serve/copy this file as-is for the
  static recorded-results view. It is also the JSON download payload.
- `assets/recorded_sample_01.png` — approved display image. SHA-256
  `916c3b694ce2c971b5d103a46a0e0031192531b35f18d83683c3308802cad484`
  (matches `input.sha256`; verified against the raw probe manifest).

**How to import (frontend owner, static path — no app/contract changes):**
1. Copy `recorded-run.json` + `assets/recorded_sample_01.png` into the
   frontend's static recorded-results folder, preserving filenames.
2. Render from `recorded-run.json` only: `mode` badge ("Recorded run — never
   live"), both invocation prompt/output pairs verbatim, timings, model
   name/revision/device/preprocessing, `human_review_note`, and
   `validation_status`. Link the image beside the record.
3. Audit labels are intentionally absent from this record (they stay in the
   probe manifest). Never join a class label onto this display.

**JSON download:** the existing `/runs/{run_id}/report` route returns only an
artifact reference (`artifact_id`/`sha256`/`kind`/`status`), not a file payload,
so it cannot serve this record without new architecture. Provide
`recorded-run.json` as the static file download instead.

**Field mapping (record → UI):**
- `recorded_run_id` → run identifier label
- `mode` ("recorded") → persistent "Recorded run — never live" banner
- `execution.started_at` / `finished_at` → actual execution timestamp
- `input.display_file` → image src; verify bytes hash `input.sha256` on import
- `input.streaming_row_index` / `dataset` / `dataset_revision` / `split` → sample identity line
- `model.name` / `model.revision` / `model.device` / `model.preprocessing` → model line
- `invocations[].task` → "caption" / "water_qa" headings; `prompt` → request text;
  `output` → unedited model output; `preprocessing_seconds` / `generation_seconds`,
  `input_token_count` / `output_token_count` → measured timing/token line
- `human_review_note` → visible review note under the caption (required)
- `validation_status` ("not_scientifically_validated") → explicit validation line
- `attribution` → dataset/model credit line
- `evidence_pointers` → reviewer links (probe commit, raw summary/invocations, manifest)

**Do-not-fabricate rules:** no confidence, no regions/boxes, no measurements,
no success claim beyond recorded execution. Caption stays quoted with its review
note. Water-QA "No." stays terse and unvalidated.
