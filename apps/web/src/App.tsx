import { Link, Route, Routes } from "react-router-dom";
import "./app.css";
import { FixtureBadge } from "./components/chrome";
import { MissionLibrary } from "./routes/MissionLibrary";
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
          <Link to="/" aria-label="Mission library" title="Missions">
            ▦
          </Link>
          <Link to="/projects/proj-delta" aria-label="Workspace" title="Workspace">
            ◉
          </Link>
          <Link to="/runs/run-success" aria-label="Run inspector" title="Runs">
            ☰
          </Link>
          <Link to="/reports/run-success" aria-label="Report" title="Report">
            ⎙
          </Link>
          <Link to="/settings" aria-label="Settings" title="Settings">
            ⚙
          </Link>
        </nav>
        <div className="main" id="main">
          <Routes>
            <Route path="/" element={<MissionLibrary />} />
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
