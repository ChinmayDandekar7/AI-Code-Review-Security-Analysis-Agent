# AI Code Review & Security Analysis Agent — Backend

Milestone 1 scope, both pieces built and tested:
1. **Code Submission Module** — paste/upload, syntax validation for Python & Java
2. **Secure Coding Knowledge Base** — chunk → embed → store → retrieve (RAG)

## Setup

```bash
cd backend
python -m venv venv

# activate:
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

## Run the API

```bash
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** — FastAPI's interactive Swagger UI.
You can test every endpoint from the browser without writing any curl commands.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/submission/paste` | Submit code as raw text (`code` required, `language` optional — auto-detected if omitted) |
| POST | `/submission/detect-language` | Live language detection as the user types (used by the frontend, debounced) |
| POST | `/submission/upload` | Submit a `.py` or `.java` file |
| GET | `/submission/{id}` | Retrieve a previously submitted CodeSubmission |
| GET | `/knowledge/search?q=...&top_k=5` | Query the secure coding knowledge base |

## Language auto-detection

`app/submission/language_detector.py` detects Python vs Java from the code's
content using weighted pattern matching (not a full parse — this matters
because it needs to work on *broken* code too, which is exactly when a
developer needs validation most). Tested against valid and syntactically
broken snippets of both languages; see the module docstring for details.
`/submission/paste` uses it automatically when no `language` is provided.

## Frontend

A React UI lives in `../frontend` and talks to this API (CORS is already
configured for `http://localhost:5173`). Run this backend first, then see
`../frontend/README.md`.

## Knowledge Base (RAG)

1. Drop OWASP / secure-coding source docs (`.md` or `.txt`) into `data/raw_docs/`.
   Two real starter docs are already included: SQL injection prevention and
   hardcoded secrets detection.
2. Run the ingestion pipeline:
   ```bash
   python -m app.knowledge_base.ingest
   ```
   This chunks each doc, embeds the chunks, and stores them in a local
   ChromaDB instance at `backend/chroma_store/` (gitignore this folder —
   it's generated data, not source).
3. Query it directly to sanity-check retrieval:
   ```bash
   python -m app.knowledge_base.retriever "how do I prevent sql injection"
   ```
4. `app/knowledge_base/retriever.py`'s `retrieve()` function is what the
   Conversational Code Assistant agent will call in a later milestone.

**On your machine**, embeddings use `sentence-transformers` (`all-MiniLM-L6-v2`),
downloaded once from Hugging Face on first run and cached locally after that —
free, no API key, runs on CPU.

## Project structure

```
backend/
  app/
    main.py                      # FastAPI app + CORS + router registration
    models.py                     # CodeSubmission, Finding, KnowledgeChunk, etc.
    submission/
      router.py                    # /submission endpoints
      validator.py                  # Python (ast) + Java (javalang) syntax checks
    knowledge_base/
      embeddings.py                 # embedding function (sentence-transformers)
      ingest.py                      # chunk -> embed -> store pipeline
      retriever.py                   # query interface for RAG
  data/raw_docs/                  # OWASP source docs live here
  requirements.txt
```

## What's been tested (actually run, not just written)

**Submission module:**
- Valid/broken Python paste → precise `Line N: message` errors via `ast`
- Valid/broken Java paste → readable errors via `javalang` (fixed a bug where
  the library's default `str(exception)` was blank on certain syntax errors —
  now pulls the real detail from `.description`/`.at`)
- `.py` file upload, unsupported file type (400), unknown submission ID (404)
- Empty/whitespace-only code → `400 "Code cannot be empty."`

**Knowledge base:**
- Ingested 2 real OWASP-style docs (SQL injection, hardcoded secrets) → 4 chunks stored
- Query "how do I prevent sql injection" → correctly ranks SQL injection chunks first
- Query "hardcoded api keys and credentials" → correctly ranks secrets chunks first
- Verified this in a network-restricted sandbox using a deterministic offline
  hashing embedder as a stand-in (see note in `embeddings.py`) — on your machine
  with internet access, `sentence-transformers` is used automatically and will
  give meaningfully better semantic retrieval than what was tested here.

## Known quirks

- Sending a truly empty string (`code=""`) via multipart form gets rejected by
  FastAPI's form parser as "missing" (422) before reaching our own empty-check.
  A whitespace-only string reaches our check correctly (400, custom message).
  Functionally both are rejected either way.
- `embeddings.py` supports `EMBEDDING_MODE=hashing` purely for offline testing.
  Leave this unset (defaults to `sentence_transformers`) on your machine.

## Next step (Milestone 2 territory)

Build the actual agents (Code Analysis, Security Vulnerability, Remediation,
PR Summary) that consume `CodeSubmission` objects and produce `Finding`
objects, using the knowledge base above for grounding security findings in
real OWASP guidance.

