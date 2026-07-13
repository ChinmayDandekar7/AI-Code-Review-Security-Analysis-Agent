import { useState } from "react";
import { searchKnowledgeBase } from "../api";
import "./KnowledgeBasePanel.css";

export default function KnowledgeBasePanel() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await searchKnowledgeBase(query);
      setResults(data.results);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="kb-panel">
      <form className="kb-search" onSubmit={handleSearch}>
        <input
          className="kb-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. how do I prevent SQL injection?"
        />
        <button className="kb-search-btn" type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p className="kb-error">{error}</p>}

      {!error && !results && (
        <p className="kb-empty">
          Query the indexed secure-coding knowledge base (OWASP guidelines, best practices).
        </p>
      )}

      {results && results.length === 0 && (
        <p className="kb-empty">No results. Has the knowledge base been ingested yet?</p>
      )}

      {results && results.length > 0 && (
        <ul className="kb-results">
          {results.map((r, i) => (
            <li key={i} className="kb-result">
              <div className="kb-result-header">
                <span className="kb-result-source">{r.source}</span>
                <span className="kb-result-distance">distance {r.distance.toFixed(3)}</span>
              </div>
              <p className="kb-result-text">{r.text.slice(0, 320)}{r.text.length > 320 ? "…" : ""}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
