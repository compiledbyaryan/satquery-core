import { useState } from "react";
import { exampleQuestions } from "../fixtures/library";

interface Props {
  pending: boolean;
  onSubmit: (question: string) => void;
  activeSummary: string;
}

export function QueryComposer({ pending, onSubmit, activeSummary }: Props): JSX.Element {
  const [q, setQ] = useState(exampleQuestions[0]);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  return (
    <form
      className="card composer"
      aria-label="Ask a question"
      onSubmit={(e) => {
        e.preventDefault();
        if (!pending && q.trim().length > 0) onSubmit(q.trim());
      }}
    >
      <div className="composer-head">
        <label htmlFor="q">
          <strong>Question</strong>
        </label>
        <span className="pill mono composer-inputs" title="Active inputs for this question">
          {activeSummary}
        </span>
      </div>
      <textarea id="q" rows={2} value={q} disabled={pending} onChange={(e) => setQ(e.target.value)} />
      <div className="composer-actions">
        <button className="btn btn-primary btn-ask" type="submit" disabled={pending || q.trim().length === 0}>
          {pending ? "Working…" : "Ask"}
        </button>
        <button
          className="btn"
          type="button"
          aria-expanded={advancedOpen}
          onClick={() => setAdvancedOpen((v) => !v)}
        >
          {advancedOpen ? "Hide examples" : "Examples"}
        </button>
      </div>
      {advancedOpen ? (
        <div className="composer-advanced">
          <label className="quiet small" htmlFor="example-q">
            Insert an example question
          </label>
          <select
            id="example-q"
            disabled={pending}
            value={exampleQuestions.includes(q) ? q : ""}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Insert an example question"
          >
            <option value="" disabled>
              Choose an example…
            </option>
            {exampleQuestions.map((x) => (
              <option key={x} value={x}>
                {x}
              </option>
            ))}
          </select>
        </div>
      ) : null}
      <p className="quiet small" style={{ marginBottom: 0 }}>
        Fixture mode answers from labelled synthetic previews. Unsupported requests (ownership, valuation, causation)
        are refused, not guessed.
      </p>
    </form>
  );
}
