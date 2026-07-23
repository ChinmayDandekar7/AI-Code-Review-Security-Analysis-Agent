import "./FindingsPanel.css";

const SEVERITY_LABELS = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
  info: "Info",
};

const AGENT_LABELS = {
  code_analysis_agent: "Code Analysis Agent",
  security_vulnerability_agent: "Security Vulnerability Agent",
};

export default function FindingsPanel({ result }) {
  if (!result) return null;

  const { findings, summary, duration_ms } = result;

  return (
    <div className="findings-panel">
      <div className="findings-header">
        <h3>Analysis Results</h3>
        <span className="findings-duration">{summary.total} findings · {duration_ms ?? "—"}ms</span>
      </div>

      <div className="severity-summary">
        {["critical", "high", "medium", "low", "info"].map((sev) => (
          <span key={sev} className={`severity-chip severity-${sev}`}>
            {SEVERITY_LABELS[sev]}: {summary[sev]}
          </span>
        ))}
      </div>

      {findings.length === 0 ? (
        <p className="findings-empty">No issues found by either agent. Clean scan.</p>
      ) : (
        <ul className="findings-list">
          {findings.map((f) => (
            <li key={f.id} className={`finding-item finding-${f.severity}`}>
              <div className="finding-top">
                <span className={`severity-badge severity-${f.severity}`}>
                  {SEVERITY_LABELS[f.severity]}
                </span>
                <span className="finding-category">{f.category}</span>
                <span className="finding-lines">
                  {f.line_start === f.line_end ? `Line ${f.line_start}` : `Lines ${f.line_start}–${f.line_end}`}
                </span>
              </div>
              <p className="finding-description">{f.description}</p>
              {f.remediation && (
                <p className="finding-remediation">
                  <strong>Fix:</strong> {f.remediation}
                </p>
              )}
              <span className="finding-agent">{AGENT_LABELS[f.agent_source] || f.agent_source}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
