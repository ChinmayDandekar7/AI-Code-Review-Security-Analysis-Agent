# AI Code Review & Security Analysis Agent

Infosys Internship project. Milestone 1 deliverables (all built and tested):

1. **System architecture, agent responsibilities, orchestration flow, data models**
   — see `Milestone1_Blueprint.md`
2. **Code Submission Module** — `backend/app/submission/` (paste + upload,
   Python & Java syntax validation) + the Submit Code view in `frontend/`
3. **Secure Coding Knowledge Base + RAG pipeline** — `backend/app/knowledge_base/`
   (chunk → embed → store → retrieve) + the Knowledge Base view in `frontend/`

## Folder layout

Place this exactly as:

```
C:\Chinmay\Infosys Internship\AI-Code-Review-Agent\
  backend\
  frontend\
  Milestone1_Blueprint.md
  README.md   (this file)
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

- Python & Java syntax validation, both valid and intentionally broken code
- **Automatic language detection** from pasted code content (no manual dropdown) —
  tested on valid and broken snippets of both languages, live badge updates as you type
- File upload (`.py`), including the correct filename and language detection
- Secure coding knowledge base ingestion (7 original source docs — OWASP Top 10,
  SQL injection, hardcoded secrets, general secure coding standards, Python
  best practices, Java best practices, code quality principles — → 20 chunks)
- Knowledge base retrieval, correctly ranking results by topic relevance across
  all 7 documents (tested with 7 different queries spanning every doc)
- Full frontend ↔ backend integration: paste → submit → results panel updates,
  upload → submit → results panel updates, Knowledge Base tab → search → results render
- Production build of the frontend (`npm run build`) completes cleanly
- Linting (`oxlint`) passes with 0 warnings

One environment-specific note: embeddings use `sentence-transformers`
(`all-MiniLM-L6-v2`), which downloads automatically from Hugging Face on first
run and requires internet access on your machine the first time you run
`ingest.py`. After that it's cached locally and works offline.

## Next milestone

Milestone 2: the actual agents (Code Analysis, Security Vulnerability,
Remediation, PR Summary) that consume `CodeSubmission` objects, produce
`Finding` objects, and are grounded in the knowledge base built here.

## License

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
