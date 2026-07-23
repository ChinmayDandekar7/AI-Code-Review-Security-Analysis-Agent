# AI Code Review & Security Analysis Agent — Backend

**Milestone 1** (built and tested):
1. **Code Submission Module** — paste/upload, syntax validation for Python & Java,
   automatic language detection
2. **Secure Coding Knowledge Base** — chunk → embed → store → retrieve (RAG),
   7 original source documents covering OWASP Top 10, secure coding standards,
   and Python/Java best practices

**Milestone 2** (built and tested):
3. **Code Analysis Agent** — code smells, complexity, design anti-patterns
   (AST-based structural analysis, Python + Java)
4. **Security Vulnerability Agent** — OWASP-standard vulnerabilities, severity-scored,
   location-specific flagging (Python + Java)
5. **Multi-agent orchestration** — Code Analysis and Security Vulnerability agents
   run in parallel via `asyncio.to_thread`, outputs merged into a unified,
   severity-sorted findings list
6. **Accuracy validation** — `tests/validate_agents.py`: 100% recall on planted
   issues across 4 vulnerable/smelly fixture files, zero false positives on
   2 clean fixture files

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python -m app.knowledge_base.ingest
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for interactive API testing.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/submission/paste` | Submit code as text (`code` required, `language` optional — auto-detected) |
| POST | `/submission/detect-language` | Live language detection as the user types |
| POST | `/submission/upload` | Submit a `.py` or `.java` file |
| GET | `/submission/{id}` | Retrieve a previously submitted CodeSubmission |
| GET | `/knowledge/search?q=...&top_k=5` | Query the secure coding knowledge base |
| POST | `/analysis/{submission_id}` | Run both agents on a submission, return findings |
| GET | `/analysis/{submission_id}` | Retrieve a previously computed analysis result |

## Milestone 2: the agents

**Code Analysis Agent** (`app/agents/code_analysis_python.py`, `code_analysis_java.py`)
AST-based structural analysis — not regex — because complexity and nesting depth
need the real parse tree to measure accurately. Detects: Long Method, Too Many
Parameters, God Class, Deep Nesting, High Cyclomatic Complexity, Mutable Default
Arguments, Bare/Swallowed Exceptions, Magic Numbers, Duplicate Code (Python);
the Java equivalents, using `javalang`'s tree plus brace-matching against the
source text for line spans (javalang doesn't track end-positions natively).

**Security Vulnerability Agent** (`app/agents/security_python.py`, `security_java.py`)
Blends AST precision (Python: checking whether an argument is a literal or
built dynamically) with pattern-based detection for cross-cutting concerns
like hardcoded secrets, consistent with the "greppable" detection approach
already documented in the knowledge base. Detects: SQL Injection, Hardcoded
Secrets, Command Injection, Insecure Deserialization, Insecure Hashing,
Dangerous Dynamic Execution (eval/exec), XSS, XXE (Java), and a low-confidence
heuristic for Possible Broken Access Control (explicitly labeled as such —
this category is fundamentally hard to confirm via static analysis alone).

**Orchestration** (`app/agents/orchestrator.py`)
Both agents run concurrently via `asyncio.to_thread` + `asyncio.gather` —
verified with a synthetic timing test showing ~2x speedup over sequential
execution, the same mechanism used for the real agents. Findings are merged,
sorted by severity then line number, and returned as a single `AnalysisResult`.

**Validation** (`tests/validate_agents.py`)
Run with `python -m tests.validate_agents`. Checks that every deliberately
planted issue across 4 fixture files is detected (100% recall), and that
2 clean fixture files produce zero findings (no false positives). This is
Milestone 2 deliverable 4.

## Known limitations (stated honestly, not hidden)

- Broken Access Control detection is a narrow, low-confidence heuristic
  (checks for auth-related hints near sensitive route handlers) — this
  category genuinely requires business-logic understanding that static
  analysis alone can't fully provide.
- The Security Vulnerability Agent's SQL injection check does lightweight
  same-function variable tracking (catches `query = "..." + x`; then
  `cursor.execute(query)`), not full taint analysis across function
  boundaries.
- XXE detection flags XML parser factory instantiation with no visible
  mitigation *anywhere in the file* — it's a "verify this" signal, not a
  confirmed vulnerability, since the mitigation could be applied elsewhere
  in a way the check doesn't see.

## Knowledge Base (RAG)

Source documents already included in `data/raw_docs/` (all original,
written for this project): `owasp_top10.md`, `sql_injection.md`,
`hardcoded_secrets.md`, `secure_coding_practices.md`,
`python_best_practices.md`, `java_best_practices.md`,
`code_quality_principles.md`. Run `python -m app.knowledge_base.ingest`
to index them (20 chunks total). Embeddings use `sentence-transformers`
(`all-MiniLM-L6-v2`), downloaded automatically on first run.

## Frontend

A React UI lives in `../frontend` and talks to this API (CORS configured
for `http://localhost:5173`). See `../frontend/README.md`.
