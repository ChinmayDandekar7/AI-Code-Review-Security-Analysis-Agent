import "./ResultsPanel.css";

export default function ResultsPanel({ submission, error, onRunAnalysis, analyzing }) {
  if (error) {
    return (
      <div className="results-panel results-panel-error">
        <div className="result-header">
          <span className="result-icon result-icon-error">✕</span>
          Request failed
        </div>
        <p className="result-message">{error}</p>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="results-panel results-panel-empty">
        <p>Submit code to see validation results here.</p>
      </div>
    );
  }

  const { is_valid_syntax, syntax_errors, language, id, filename } = submission;

  return (
    <div className={`results-panel ${is_valid_syntax ? "results-panel-ok" : "results-panel-warn"}`}>
      <div className="result-header">
        <span className={`result-icon ${is_valid_syntax ? "result-icon-ok" : "result-icon-warn"}`}>
          {is_valid_syntax ? "✓" : "!"}
        </span>
        {is_valid_syntax ? "Syntax valid" : `${syntax_errors.length} syntax issue${syntax_errors.length === 1 ? "" : "s"} found`}
      </div>

      <div className="result-meta">
        <span className="result-pill">{language}</span>
        {filename && <span className="result-pill result-pill-muted">{filename}</span>}
        <span className="result-id">id: {id.slice(0, 8)}</span>
      </div>

      {!is_valid_syntax && (
        <ul className="problem-list">
          {syntax_errors.map((err, i) => (
            <li key={i} className="problem-item">
              <span className="problem-marker" aria-hidden="true" />
              {err}
            </li>
          ))}
        </ul>
      )}

      {is_valid_syntax && onRunAnalysis && (
        <button className="run-analysis-btn" onClick={onRunAnalysis} disabled={analyzing}>
          {analyzing ? "Running agents…" : "Run Code Analysis + Security Scan"}
        </button>
      )}
    </div>
  );
}
