import "./StatusBar.css";

export default function StatusBar({ language, charCount, lineCount, status }) {
  return (
    <footer className="statusbar">
      <div className="statusbar-left">
        <span className="statusbar-item">{language}</span>
        <span className="statusbar-item">
          Ln {lineCount}, {charCount} chars
        </span>
      </div>
      <div className="statusbar-right">
        <span className="statusbar-item">{status}</span>
      </div>
    </footer>
  );
}
