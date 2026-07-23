import { useEffect, useState } from "react";
import TitleBar from "./components/TitleBar";
import TabStrip from "./components/TabStrip";
import CodeEditor from "./components/CodeEditor";
import UploadZone from "./components/UploadZone";
import ResultsPanel from "./components/ResultsPanel";
import FindingsPanel from "./components/FindingsPanel";
import StatusBar from "./components/StatusBar";
import KnowledgeBasePanel from "./components/KnowledgeBasePanel";
import LanguageBadge from "./components/LanguageBadge";
import {
  submitPastedCode,
  submitUploadedFile,
  checkHealth,
  detectLanguage,
  runAnalysis,
} from "./api";
import "./App.css";

const VIEW_TABS = [
  { id: "submit", label: "Submit Code" },
  { id: "knowledge", label: "Knowledge Base" },
];

const MODE_TABS = [
  { id: "paste", label: "Paste" },
  { id: "upload", label: "Upload" },
];

const DETECT_DEBOUNCE_MS = 400;

export default function App() {
  const [connected, setConnected] = useState(false);
  const [view, setView] = useState("submit");
  const [mode, setMode] = useState("paste");
  const [code, setCode] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [file, setFile] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => setConnected(true))
      .catch(() => setConnected(false));
  }, []);

  // Debounced live language auto-detection as the user types.
  useEffect(() => {
    if (mode !== "paste" || !code.trim()) {
      setDetectedLanguage(null);
      return;
    }
    setDetecting(true);
    const timer = setTimeout(() => {
      detectLanguage(code)
        .then((data) => setDetectedLanguage(data.language))
        .catch(() => setDetectedLanguage(null))
        .finally(() => setDetecting(false));
    }, DETECT_DEBOUNCE_MS);

    return () => clearTimeout(timer);
  }, [code, mode]);

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    setSubmission(null);
    setAnalysisResult(null);
    setAnalysisError(null);
    try {
      let result;
      if (mode === "paste") {
        result = await submitPastedCode(code);
      } else {
        if (!file) {
          setError("Choose a .py or .java file first.");
          setSubmitting(false);
          return;
        }
        result = await submitUploadedFile(file);
      }
      setSubmission(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRunAnalysis() {
    if (!submission) return;
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const result = await runAnalysis(submission.id);
      setAnalysisResult(result);
    } catch (err) {
      setAnalysisError(err.message);
    } finally {
      setAnalyzing(false);
    }
  }

  const lineCount = code ? code.split("\n").length : 1;
  const canSubmit = mode === "paste" ? code.trim().length > 0 : !!file;
  const statusLanguage = detectedLanguage || "auto";

  return (
    <div className="app">
      <TitleBar connected={connected} />
      <TabStrip tabs={VIEW_TABS} active={view} onChange={setView} />

      <main className="app-main">
        {view === "submit" ? (
          <div className="submit-layout">
            <div className="submit-left">
              <div className="mode-row">
                <TabStrip tabs={MODE_TABS} active={mode} onChange={setMode} />
                {mode === "paste" && (
                  <LanguageBadge language={detectedLanguage} detecting={detecting} />
                )}
              </div>

              {mode === "paste" ? (
                <CodeEditor
                  value={code}
                  onChange={setCode}
                  placeholder="Paste your Python or Java code here — language is detected automatically…"
                />
              ) : (
                <UploadZone
                  selectedFile={file}
                  onFileSelected={(f, err) => {
                    setFile(f);
                    if (err) setError(err);
                  }}
                />
              )}

              <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={!canSubmit || submitting}
              >
                {submitting ? "Validating…" : "Submit for validation"}
              </button>
            </div>

            <div className="submit-right">
              <ResultsPanel
                submission={submission}
                error={error}
                onRunAnalysis={handleRunAnalysis}
                analyzing={analyzing}
              />
              {analysisError && <p className="analysis-error">{analysisError}</p>}
              <FindingsPanel result={analysisResult} />
            </div>
          </div>
        ) : (
          <KnowledgeBasePanel />
        )}
      </main>

      {view === "submit" && mode === "paste" && (
        <StatusBar
          language={statusLanguage}
          charCount={code.length}
          lineCount={lineCount}
          status={submission ? (submission.is_valid_syntax ? "Valid" : "Errors found") : "Ready"}
        />
      )}
    </div>
  );
}
