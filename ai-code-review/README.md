# AI Code Review & Security Analysis Agent

Infosys Internship project.

## Milestone 1 (complete)
1. System architecture, agent responsibilities, orchestration flow, data
   models — see `Milestone1_Blueprint.md`
2. Code Submission Module — paste + upload, Python & Java, syntax validation,
   automatic language detection
3. Secure Coding Knowledge Base + RAG pipeline — 7 original source documents,
   chunked, embedded, indexed in ChromaDB

## Milestone 2 (complete)
1. Code Analysis Agent — code smells, complexity, design anti-patterns,
   severity-scored per finding (AST-based, Python + Java)
2. Security Vulnerability Agent — OWASP-standard vulnerabilities, classified
   by type and severity, location-specific flagging (Python + Java)
3. Multi-agent orchestration — both agents run in parallel
   (`asyncio.to_thread`), outputs merged into a unified findings list
4. Accuracy validation — `backend/tests/validate_agents.py`, 100% recall on
   planted issues across 4 fixtures, zero false positives on clean code

## Folder layout

```
C:\Chinmay\Infosys Internship\AI-Code-Review-Agent\
  backend\
  frontend\
  Milestone1_Blueprint.md
  README.md
  LICENSE
  .gitignore
```

## Running it locally (Windows / VS Code)

**Terminal 1 — backend:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m app.knowledge_base.ingest
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open **http://localhost:5173**. Backend API docs at **http://127.0.0.1:8000/docs**.

## What's actually been verified

Everything below was run and observed working, not just written:

**Milestone 1:**
- Python & Java syntax validation, valid and intentionally broken code
- Automatic language detection from code content, tested on valid and
  broken snippets of both languages
- File upload, correct filename and language detection
- Knowledge base: 7 docs → 20 chunks, retrieval correctly ranks results
  by topic relevance across all documents
- Full frontend ↔ backend integration (paste, upload, knowledge search)

**Milestone 2:**
- Code Analysis Agent: 13 distinct checks (Python + Java combined) tested
  against fixtures with deliberately planted issues — every category
  detected, zero false positives on clean code
- Security Vulnerability Agent: 15 distinct checks (Python + Java combined)
  tested the same way, including "safe" counterpart functions to confirm
  no false positives (parameterized queries, `shell=False`, `bcrypt`, etc.)
- Multi-agent orchestration: verified via the real HTTP API
  (`POST /analysis/{id}`) end to end, and parallelism specifically confirmed
  with a synthetic timing test (~2x speedup over sequential execution)
- Formal accuracy harness (`validate_agents.py`): 100% recall across all
  4 vulnerable/smelly fixtures, 0 false positives across 2 clean fixtures
- Frontend Findings Panel: verified via a real browser driving the actual
  running app — vulnerable Python (10 findings) and vulnerable Java
  (7 findings) both correctly submitted, analyzed, and displayed with
  severity badges and remediation text; real per-request duration shown
  (e.g. 22.64ms), not a placeholder

One environment-specific note: embeddings use `sentence-transformers`,
which downloads automatically from Hugging Face on first run and requires
internet access on your machine at that point. After that it's cached
locally and works offline.

## Next milestone

Milestone 3 territory (not yet started): Remediation Agent, PR Summary
Agent, Conversational Code Assistant, and exportable review reports. A
basic Findings Display UI was already built as part of Milestone 2 (severity
badges, remediation text per finding) to make the agents demoable — a fuller
version with filtering/sorting/export could still be a Milestone 3 refinement.

## License

MIT — see [LICENSE](LICENSE).
