# AI Code Review & Security Analysis Agent
## Milestone 1 Blueprint (Week 1–2)

This document was written as the initial design plan before any code
existed, covering system architecture, agent responsibilities, orchestration
flow, and data models — Milestone 1 deliverable 1.

---

## Implementation Status (as built)

The actual implementation follows this plan closely, with refinements made
during development:

1. **Language selection is fully automatic**, not manual. `app/submission/
   language_detector.py` detects Python vs. Java directly from the code's
   content (weighted pattern matching, tested against valid *and*
   syntactically broken snippets of both languages).
2. **The knowledge base has 7 source documents**: `owasp_top10.md`,
   `sql_injection.md`, `hardcoded_secrets.md`, `secure_coding_practices.md`,
   `python_best_practices.md`, `java_best_practices.md`,
   `code_quality_principles.md` — 20 chunks total, all original content.
3. A working React + Vite frontend was built on top of this backend plan.

Milestone 2 added the Code Analysis Agent, Security Vulnerability Agent,
multi-agent orchestration, and a formal accuracy validation harness — see
`backend/README.md` for details on that layer.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + FastAPI | Native fit for AST parsing, async endpoints |
| LLM (future milestones) | Claude API | Reasoning-heavy agents (Remediation, Conversational Assistant) |
| Java parsing | `javalang` | Pure-Python, no JVM dependency |
| Python parsing | `ast` (built-in) | Structural analysis without extra dependencies |
| Vector store | ChromaDB (local, embedded) | Free, no server to host |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | Free, local, no API key |
| Frontend | React + Vite | Fast iteration, matches existing full-stack comfort |

## System Architecture

```
Frontend (React)
   │  REST
Backend (FastAPI)
   │
   ├── Code Submission Module
   │      paste/upload → language auto-detect → syntax validation
   │      → CodeSubmission stored
   │
   ├── Multi-Agent Orchestrator (Milestone 2)
   │      runs in parallel:
   │        ├── Code Analysis Agent (code smells, complexity)
   │        └── Security Vulnerability Agent (OWASP vulnerabilities)
   │      merges → sorted Finding list → AnalysisResult
   │
   └── Secure Coding Knowledge Base (RAG)
          OWASP + best-practice docs → chunked → embedded → ChromaDB
          → retrieve() queried by search API (and, in later milestones,
            the Conversational Code Assistant)
```

## Data Models

```python
class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"

class CodeSubmission(BaseModel):
    id: str
    language: Language
    method: SubmissionMethod  # paste | upload
    raw_code: str
    filename: str | None
    submitted_at: datetime
    is_valid_syntax: bool
    syntax_errors: list[str]

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    id: str
    submission_id: str
    agent_source: str          # e.g. "security_vulnerability_agent"
    category: str               # e.g. "SQL Injection"
    severity: Severity
    line_start: int
    line_end: int
    description: str
    remediation: str | None
    fixed_code_snippet: str | None

class AnalysisResult(BaseModel):
    submission_id: str
    analyzed_at: datetime
    findings: list[Finding]
    summary: dict                # counts per severity + total
```

## Build Order (as followed)

1. **Research** — OWASP Top 10, secure coding guidelines, code smell
   catalogue, RAG architecture basics
2. **Architecture & data models** — locked in above before writing code
3. **Code Submission Module** — validator (Python `ast` / Java `javalang`),
   API endpoints, auto-detection
4. **Secure Coding Knowledge Base** — chunking, embedding, ChromaDB indexing,
   retrieval, HTTP search endpoint
5. **Frontend** — React UI for submission and knowledge base search
6. **(Milestone 2) Agents + orchestration + validation**

## Milestone 1 Checklist

- [x] Architecture diagram + data models locked in
- [x] `validator.py` working for both Python and Java, tested with
      intentionally broken code
- [x] `/submission/paste` and `/submission/upload` returning correct
      `CodeSubmission` objects
- [x] Language auto-detected from code content, no manual selection required
- [x] Frontend paste/upload UI wired to backend, plus Knowledge Base search
- [x] 7 original secure-coding source documents written and saved
- [x] `ingest.py` run successfully — 20 chunks in ChromaDB
- [x] `retriever.py` returns relevant chunks for test queries across all
      7 documents, exposed over HTTP at `GET /knowledge/search`

## Next Steps

Milestone 1 and Milestone 2 are both complete. Milestone 3 territory:
Remediation Agent, PR Summary Agent, Conversational Code Assistant,
Findings Display UI, and exportable review reports.
