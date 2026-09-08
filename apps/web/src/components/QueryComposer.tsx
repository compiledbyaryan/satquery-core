import { useState } from "react";
import { exampleQuestions } from "../fixtures/library";

interface Props {
  pending: boolean;
  onSubmit: (question: string) => void;
}

export function QueryComposer({ pending, onSubmit }: Props): JSX.Element {
  const [q, setQ] = useState(exampleQuestions[0]);
  return (
    <form
      className="card"
      aria-label="Ask a question"
      onSubmit={(e) => {
        e.preventDefault();
        if (!pending && q.trim().length > 0) onSubmit(q.trim());
      }}
    >
      <label htmlFor="q">
        <strong>Question</strong>
      </label>
      <textarea id="q" rows={2} value={q} disabled={pending} onChange={(e) => setQ(e.target.value)} />
      <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap", alignItems: "center" }}>
        <button className="btn btn-primary" type="submit" disabled={pending || q.trim().length === 0}>
          {pending ? "Working…" : "Ask"}
        </button>
        <label className="quiet small" htmlFor="example-q">
          Example
        </label>
        <select
          id="example-q"
          disabled={pending}
          value={exampleQuestions.includes(q) ? q : ""}
          onChange={(e) => setQ(e.target.value)}
          style={{ maxWidth: 420 }}
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
      <p className="quiet small" style={{ marginBottom: 0 }}>
        Fixture mode answers from labelled synthetic previews. Unsupported requests (ownership, valuation, causation)
        are refused, not guessed.
      </p>
    </form>
  );
}
