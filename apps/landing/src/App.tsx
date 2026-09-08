import "./style.css";
function workspaceHref(): string {
  const port = window.location.port;
  if (port === "5174") return `${window.location.protocol}//${window.location.hostname}:5173/app/projects/proj-delta`;
  if (port === "4174") return `${window.location.protocol}//${window.location.hostname}:4173/app/projects/proj-delta`;
  return "/app/projects/proj-delta";
}
export function App(): JSX.Element {
  return <div className="page">
    <a className="skip-link" href="#cta">Skip to workspace link</a>
    <header className="site-header"><a className="brand" href="/" aria-label="SatQuery home"><svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true"><circle cx="14" cy="14" r="9" stroke="currentColor" strokeWidth="1.5"/><path d="M14 0v9M14 19v9M0 14h9M19 14h9" stroke="currentColor" strokeWidth="1.5"/></svg><span>SatQuery</span></a><span className="header-note">Earth observation / Field Desk</span></header>
    <main className="hero">
      <section className="hero-copy"><h1>Ask Earth.<br/><em>Inspect</em><br/>the evidence.</h1>
        <p className="lede">An observation is a starting point. Follow a question through to its source, its interpretation, and its limits.</p>
        <a id="cta" className="cta" href={workspaceHref()}>Open workspace <span aria-hidden="true">↗</span></a>
        <p className="mode-note">Interactive synthetic examples.<br/>Recorded model output, with human review.</p>
      </section>
      <figure className="hero-visual">
        <svg viewBox="0 0 640 720" aria-hidden="true" focusable="false">
          <defs><clipPath id="earth"><circle cx="340" cy="337" r="258"/></clipPath></defs>
          <circle cx="340" cy="337" r="258" fill="#263e32" stroke="#91a68a" strokeWidth="1"/>
          <g clipPath="url(#earth)" fill="none" stroke="#a9bb8d" strokeWidth="1.1">
            {Array.from({length:19},(_,i)=><path key={i} transform={`translate(${i*9-75} ${i*16-140})`} d="M-20 475 C35 370 65 540 145 421 S195 197 260 253 S322 425 374 315 S361 125 425 149 S516 274 554 169 S582 30 690 94" opacity={i%3===0 ? .9 : .42}/>)}
            {Array.from({length:10},(_,i)=><path key={i} transform={`translate(${i*13-40} ${i*14})`} d="M75 481 C187 384 220 597 297 478 S365 441 435 479 S513 494 634 382" opacity=".35"/>)}
          </g>
          <ellipse cx="340" cy="337" rx="306" ry="107" transform="rotate(-32 340 337)" fill="none" stroke="#c7df5a" strokeWidth="1.5"/>
          <circle cx="116" cy="481" r="5" fill="#c7df5a"/>
          <path d="M340 37v30M340 607v30M40 337h30M610 337h30" stroke="#8b9e7f"/>
          <path d="M41 658h558" stroke="#52694f"/>
        </svg>
        <figcaption><span>Contour study</span><span>Decorative illustration · not satellite imagery</span></figcaption>
      </figure>
    </main>
    <footer className="site-footer"><span>From observation to an inspectable answer.</span><span>Internal demo · Live analysis is not connected</span></footer>
  </div>;
}
