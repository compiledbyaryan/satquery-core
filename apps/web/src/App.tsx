import { Link, NavLink, Route, Routes } from "react-router-dom";
import "./app.css";
import { FixtureBadge } from "./components/chrome";
import { MissionLibrary } from "./routes/MissionLibrary";
import { RecordedRunView } from "./routes/RecordedRunView";
import { ReportView } from "./routes/ReportView";
import { RunInspector } from "./routes/RunInspector";
import { Settings } from "./routes/Settings";
import { Workspace } from "./routes/Workspace";

export function App(): JSX.Element {
  return (
    <div>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <FixtureBadge mode="UI prototype — synthetic fixtures" />
      <div className="app-shell">
        <nav className="rail" aria-label="Field Desk">
          <NavLink to="/" aria-label="Mission library" title="Missions">
            <span aria-hidden="true" className="rail-glyph">▦</span>
            <span className="rail-label">Missions</span>
          </NavLink>
          <NavLink to="/projects/proj-delta" aria-label="Workspace" title="Workspace">
            <span aria-hidden="true" className="rail-glyph">◉</span>
            <span className="rail-label">Workspace</span>
          </NavLink>
          <NavLink to="/runs/run-success" aria-label="Run inspector" title="Runs">
            <span aria-hidden="true" className="rail-glyph">☰</span>
            <span className="rail-label">Runs</span>
          </NavLink>
          <NavLink to="/reports/run-success" aria-label="Report" title="Report">
            <span aria-hidden="true" className="rail-glyph">⎙</span>
            <span className="rail-label">Report</span>
          </NavLink>
          <NavLink to="/settings" aria-label="Settings" title="Settings">
            <span aria-hidden="true" className="rail-glyph">⚙</span>
            <span className="rail-label">Settings</span>
          </NavLink>
        </nav>
        <div className="main" id="main">
          <Routes>
            <Route path="/" element={<MissionLibrary />} />
            <Route path="/recorded/run-01" element={<RecordedRunView />} />
            <Route path="/projects/:id" element={<Workspace />} />
            <Route path="/runs/:id" element={<RunInspector />} />
            <Route path="/reports/:id" element={<ReportView />} />
            <Route path="/settings" element={<Settings />} />
            <Route
              path="*"
              element={
                <div className="page">
                  <h1>Not found</h1>
                  <p className="quiet">
                    Unknown workbench route. <Link to="/">Return to the mission library.</Link>
                  </p>
                </div>
              }
            />
          </Routes>
        </div>
      </div>
    </div>
  );
}
