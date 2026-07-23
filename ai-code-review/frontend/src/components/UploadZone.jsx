import { useRef, useState } from "react";
import "./UploadZone.css";

export default function UploadZone({ onFileSelected, selectedFile }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  function handleFiles(fileList) {
    const file = fileList?.[0];
    if (!file) return;
    if (!file.name.endsWith(".py") && !file.name.endsWith(".java")) {
      onFileSelected(null, "Only .py and .java files are supported.");
      return;
    }
    onFileSelected(file, null);
  }

  return (
    <div
      className={`upload-zone ${dragActive ? "upload-zone-active" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragActive(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".py,.java"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
      {selectedFile ? (
        <>
          <div className="upload-filename">{selectedFile.name}</div>
          <div className="upload-hint">Click or drop to replace</div>
        </>
      ) : (
        <>
          <div className="upload-icon" aria-hidden="true">↑</div>
          <div className="upload-primary">Drop a .py or .java file here</div>
          <div className="upload-hint">or click to browse</div>
        </>
      )}
    </div>
  );
}
