import { Link } from "react-router-dom";
import type { RunEventView } from "../viewmodel/types";

export function FixtureBadge({ mode }: { mode: string }): JSX.Element {
  return (
    <div className="fixture-strip" role="note" aria-label="Execution mode">
      <span>
        <strong>{mode}</strong>
        <span className="quiet" style={{ color: "#d8ded2" }}>
          {" "}
          {mode.startsWith("Recorded") ? " · Original model output with human review" : " · Supplied examples, no live backend"}
        </span>
      </span>
      <Link to="/settings">Why labelled?</Link>
    </div>
  );
}

export function ProgressStrip({ events, status }: { events: RunEventView[]; status: string }): JSX.Element {
  if (events.length === 0) return <p className="quiet small">No stages yet — submit a question to begin.</p>;
  return (
    <div className="progress-strip" role="status" aria-label={`Investigation stage: ${status}`}>
      {events.map((e) => (
        <span key={e.id} className="stage" data-state={e.state}>
          {e.label}: {e.state}
        </span>
      ))}
    </div>
  );
}
