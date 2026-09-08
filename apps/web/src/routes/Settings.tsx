export function Settings(): JSX.Element {
  return (
    <div className="page">
      <h1 style={{ marginTop: 0 }}>Data &amp; runtime settings</h1>
      <div className="card">
        <strong>Provider readiness (fixture mode)</strong>
        <ul className="small">
          <li>Real optical specialist: unavailable — fixtures cannot substitute.</li>
          <li>Real SAR/temporal specialists: unavailable.</li>
          <li>Local/private mode: fixture previews only; nothing uploaded.</li>
        </ul>
      </div>
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Job limits &amp; retention (illustrative)</strong>
        <p className="quiet small" style={{ marginBottom: 0 }}>
          One GPU job at a time in the real pilot; fixture mode runs no jobs. No secret values are shown on this
          screen.
        </p>
      </div>
      <div className="card" style={{ marginTop: 10 }}>
        <strong>Why “UI prototype — synthetic fixtures”?</strong>
        <p className="quiet small" style={{ marginBottom: 0 }}>
          Backend routes are incomplete and no live integration is assumed. The persistent label distinguishes
          implemented, planned, synthetic-fixture, and recorded behavior per project truth rules.
        </p>
      </div>
    </div>
  );
}
