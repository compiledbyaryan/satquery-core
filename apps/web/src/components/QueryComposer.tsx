import { demoQuestions } from "../logic/demo";
interface Props {
  pending: boolean; question: string; onChange: (question: string) => void;
  onSubmit: (question: string) => void; activeSummary: string;
}
export function QueryComposer({ pending, question, onChange, onSubmit, activeSummary }: Props): JSX.Element {
  return <form className="composer" aria-label="Ask a question" onSubmit={e => { e.preventDefault(); if (!pending && question.trim()) onSubmit(question.trim()); }}>
    <div className="composer-head"><label htmlFor="q">Ask about this observation</label><span className="quiet small">Interactive fixture</span></div>
    <p className="quiet small input-summary">{activeSummary}</p>
    <textarea id="q" rows={2} value={question} disabled={pending} onChange={e => onChange(e.target.value)} />
    <div className="composer-actions">
      <button className="btn btn-primary btn-ask" type="submit" disabled={pending || !question.trim()}>{pending ? "Simulating example…" : "Run example"}<span aria-hidden="true"> ↗</span></button>
      <label className="sr-only" htmlFor="example-q">Example question</label>
      <select id="example-q" disabled={pending} value={demoQuestions.includes(question) ? question : ""} onChange={e => onChange(e.target.value)}>
        <option value="" disabled>Choose a supported example</option>
        {demoQuestions.map((q, i) => <option key={q} value={q}>{["Change illustration", "Optical + SAR · partial", "Caption · unavailable", "Tool failure · simulated"][i]}</option>)}
      </select>
    </div>
    <p className="quiet small">Supplied answers only. Other questions return an unsupported response.</p>
  </form>;
}
