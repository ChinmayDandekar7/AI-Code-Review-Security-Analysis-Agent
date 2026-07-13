import { useRef } from "react";
import "./CodeEditor.css";

export default function CodeEditor({ value, onChange, placeholder }) {
  const gutterRef = useRef(null);
  const textareaRef = useRef(null);

  const lineCount = value ? value.split("\n").length : 1;
  const lines = Array.from({ length: lineCount }, (_, i) => i + 1);

  function syncScroll() {
    if (gutterRef.current && textareaRef.current) {
      gutterRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  }

  return (
    <div className="code-editor">
      <div className="code-gutter" ref={gutterRef} aria-hidden="true">
        {lines.map((n) => (
          <div key={n} className="gutter-line">
            {n}
          </div>
        ))}
      </div>
      <textarea
        ref={textareaRef}
        className="code-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onScroll={syncScroll}
        placeholder={placeholder}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
      />
    </div>
  );
}
