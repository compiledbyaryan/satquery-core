import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { SafeImage } from "../components/SafeImage";
import {
  RECORDED_IMAGE_SHA256,
  RECORDED_IMAGE_URL,
  RECORDED_RUN_URL,
  parseRecordedRun,
  type RecordedRun
} from "../recorded/types";

/** Recorded model run: renders the published JSON record verbatim.
 *  No processing animation, no success claim, no invented regions/confidence. */
export function RecordedRunView(): JSX.Element {
  const [record, setRecord] = useState<RecordedRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(RECORDED_RUN_URL, { headers: { Accept: "application/json" } })
      .then((res) => {
        if (!res.ok) throw new Error(`Record unavailable (HTTP ${res.status})`);
        return res.json() as Promise<unknown>;
      })
      .then((raw) => {
        if (!cancelled) setRecord(parseRecordedRun(raw));
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Record unavailable");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="page recorded">
      <p>
        <Link to="/">← Back to mission library</Link>
      </p>
      <div className="recorded-banners" role="note" aria-label="Recorded run status">
        <span className="tag tag-model">Recorded run — not live analysis</span>
        <span className="tag tag-unknown">Not scientifically validated</span>
      </div>
      <h1 style={{ marginTop: 8 }}>Recorded model run</h1>
      {error ? (
        <div className="notice error" role="alert">
          Could not load the recorded run: {error}. The static record may be missing from this build.
        </div>
      ) : record === null ? (
        <p className="quiet" role="status">
          Loading the recorded run…
        </p>
      ) : (
        <article aria-label={`Recorded run ${record.recorded_run_id}`}>
          <p className="quiet small mono">
            {record.recorded_run_id} · executed {record.execution.started_at} → {record.execution.finished_at}
          </p>
          <div className="recorded-grid">
            <figure className="card recorded-figure">
              <SafeImage src={RECORDED_IMAGE_URL} alt="Recorded EuroSAT sample 01 (64 by 64 pixel RGB preview)" />
              <figcaption className="quiet small">
                Actual source image · {record.input.size_px[0]}×{record.input.size_px[1]} px{" "}
                {record.input.source_mode} · {record.input.dataset} · split {record.input.split} · row{" "}
                {record.input.streaming_row_index}
                <br />
                SHA-256 <span className="mono">{record.input.sha256}</span>
                {record.input.sha256 === RECORDED_IMAGE_SHA256 ? " (verified on import)" : " (MISMATCH)"}
              </figcaption>
            </figure>
            <div className="card">
              <strong>Model &amp; execution (measured)</strong>
              <dl className="small recorded-dl">
                <dt>Model</dt>
                <dd>
                  {record.model.name} · rev <span className="mono">{record.model.revision.slice(0, 12)}…</span>
                </dd>
                <dt>Device</dt>
                <dd>
                  {record.model.device} (torch CUDA available:{" "}
                  {record.execution.torch_cuda_available ? "yes" : "no"})
                </dd>
                <dt>Wall time</dt>
                <dd className="mono">
                  {record.execution.elapsed_seconds_total.toFixed(1)}s total · load{" "}
                  {record.execution.load_seconds.toFixed(1)}s
                </dd>
                <dt>Parameters</dt>
                <dd className="mono">{record.model.parameter_count.toLocaleString("en-US")}</dd>
              </dl>
            </div>
          </div>

          {record.invocations.map((inv) => (
            <section key={inv.task} className="card recorded-invocation" aria-label={`Recorded ${inv.task}`}>
              <h2>
                {inv.task === "caption" ? "Caption (verbatim model output)" : "Water question (verbatim model output)"}
              </h2>
              <p className="quiet small">Request</p>
              <blockquote className="recorded-quote">{inv.prompt}</blockquote>
              <p className="quiet small">Model response (unedited)</p>
              <blockquote className="recorded-quote recorded-output">“{inv.output}”</blockquote>
              <p className="quiet small mono">
                preprocessing {inv.preprocessing_seconds.toFixed(1)}s · generation{" "}
                {inv.generation_seconds.toFixed(1)}s · tokens in {inv.input_token_count} / out{" "}
                {inv.output_token_count}
              </p>
            </section>
          ))}

          <section className="card recorded-review" aria-label="Human review">
            <h2>Human review (required)</h2>
            <p>{record.human_review_note}</p>
            <p className="quiet small">
              This note is human review, not automatic hallucination detection. The caption above is an
              unvalidated model utterance — it is quoted for inspection and must not be shown as a
              supported finding. No regions, confidence, or measurements are claimed for this run.
            </p>
          </section>

          <section className="card" aria-label="Attribution and evidence">
            <h2>Attribution &amp; evidence</h2>
            <ul className="small">
              <li>Dataset: {record.attribution.dataset}</li>
              <li>Model: {record.attribution.model}</li>
              <li>
                Validation: <span className="mono">{record.validation_status}</span>
              </li>
              <li>
                Probe commit: <span className="mono">{record.evidence_pointers.probe_commit}</span> · source
                commit <span className="mono">{record.source_commit}</span>
              </li>
            </ul>
            <div className="recorded-actions">
              <a className="btn btn-primary" href={RECORDED_RUN_URL} download="recorded-run.json">
                Download run JSON
              </a>
              <span className="quiet small">PDF export unavailable — explained, not a dead button.</span>
            </div>
          </section>
        </article>
      )}
    </div>
  );
}
