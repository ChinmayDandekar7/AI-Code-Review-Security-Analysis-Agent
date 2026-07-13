import "./TitleBar.css";

export default function TitleBar({ connected }) {
  return (
    <header className="titlebar">
      <div className="titlebar-left">
        <span className="titlebar-dots" aria-hidden="true">
          <span />
          <span />
          <span />
        </span>
        <span className="titlebar-title">
          AI Code Review <span className="titlebar-amp">&amp;</span> Security Analysis Agent
        </span>
      </div>
      <div className="titlebar-right">
        <span className={`conn-dot ${connected ? "conn-on" : "conn-off"}`} aria-hidden="true" />
        <span className="conn-label">{connected ? "Backend connected" : "Backend unreachable"}</span>
      </div>
    </header>
  );
}
