import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import "./app.css";
import { FixtureBadge } from "./components/chrome";
import { MissionLibrary } from "./routes/MissionLibrary";
import { RecordedRunView } from "./routes/RecordedRunView";
import { ReportView } from "./routes/ReportView";
import { RunInspector } from "./routes/RunInspector";
import { Settings } from "./routes/Settings";
import { Workspace } from "./routes/Workspace";

export function App(): JSX.Element {
  const recorded = useLocation().pathname.startsWith("/recorded/");
  return (
    <div>
      <a className="skip-link" href="#main">
        Skip to main content
      </a>
      <FixtureBadge mode={recorded ? "Recorded run—not live analysis" : "Interactive demo · synthetic fixtures"} />
      <div className="app-shell">
        <nav className="rail" aria-label="Field Desk">
          <NavLink to="/" aria-label="Mission library" title="Missions">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" /></svg>
            <span className="rail-label">Missions</span>
          </NavLink>
          <NavLink to="/projects/proj-delta" aria-label="Workspace" title="Workspace">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><circle cx="12" cy="12" r="8"/><path d="M12 1v6M12 17v6M1 12h6M17 12h6"/></svg>
            <span className="rail-label">Workspace</span>
          </NavLink>
          <NavLink to="/recorded/run-01" aria-label="Recorded inference" title="Recorded inference">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M6 3h12v18H6zM9 8h6M9 12h6M9 16h3" /></svg><span className="rail-label">Recorded</span>
          </NavLink>
          <NavLink to="/settings" aria-label="Settings" title="Settings">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/><path d="M8 3v6M16 9v6M10 15v6"/></svg>
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
