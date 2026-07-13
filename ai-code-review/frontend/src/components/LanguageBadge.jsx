import "./LanguageBadge.css";

const LABELS = {
  python: "Python",
  java: "Java",
};

export default function LanguageBadge({ language, detecting }) {
  if (detecting) {
    return <span className="lang-badge lang-badge-detecting">detecting…</span>;
  }
  if (!language) {
    return <span className="lang-badge lang-badge-idle">auto-detect</span>;
  }
  return (
    <span className={`lang-badge lang-badge-${language}`}>
      <span className="lang-badge-dot" aria-hidden="true" />
      {LABELS[language] || language}
    </span>
  );
}
