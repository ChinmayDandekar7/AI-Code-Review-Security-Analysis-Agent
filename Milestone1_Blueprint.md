# AI Code Review & Security Analysis Agent
## Milestone 1 Blueprint (Week 1–2)

This is our working reference for Milestone 1. Everything below maps directly to the 4 deliverables in your project brief. Keep this open while you build — each section is written so you can follow it step by step without needing extra context.

---

## 0. Recommended Tech Stack (near-zero cost)

| Layer | Choice | Why |
|---|---|---|
| Backend / Agent orchestration | **Python + FastAPI** | Native fit for AST parsing (Python's `ast`), async endpoints, easy LLM SDK integration |
| LLM for agents | **Claude API** (`claude-sonnet-4-6` or similar) | Strong reasoning on code, generous free/dev-tier usage for a student project |
| Agent framework | **LangGraph** (or plain function-calling if you want to avoid the abstraction) | Clean way to model 5 agents as nodes in a pipeline |
| Java parsing | **javalang** (pure-Python Java parser) | No JVM dependency, good enough for structure/smell detection |
| Python parsing | **`ast` (built-in) + `astroid`** | `astroid` gives richer static-analysis-friendly nodes than raw `ast` |
| Vector store | **ChromaDB** (local, embedded) | Free, no server to host, perfect for MVP scale |
| Embeddings | **`sentence-transformers/all-MiniLM-L6-v2`** (local) or Claude/Voyage embeddings if you want hosted | Free and fast locally; swap later if quality needs improve |
| Frontend | **React + Vite** (or Next.js if you want SSR/deploy simplicity) | Matches your existing full-stack comfort zone |
| File/code storage | Local filesystem for MVP → Supabase later if you need persistence across sessions | Keeps Milestone 1 dependency-free |

> This is a proposal, not a mandate — if your course requires a specific stack (e.g., Java for backend, or a specific vector DB), tell me and I'll re-map everything below to that stack.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                       │
│   Code Submission UI  →  Findings Dashboard  →  Chat Assistant  │
└───────────────────────────────┬─────────────────────────────────┘
                                 │ REST/WebSocket
┌───────────────────────────────▼─────────────────────────────────┐
│                        FASTAPI BACKEND                          │
│                                                                   │
│  ┌────────────────────┐        ┌─────────────────────────────┐ │
│  │ Code Submission      │        │  Orchestrator (LangGraph)    │ │
│  │ Module               │──────▶│  runs agents in sequence/     │ │
│  │ - paste/upload        │        │  parallel per pipeline design│ │
│  │ - language detect     │        └──────┬───────┬───────┬──────┘ │
│  │ - syntax validation   │               │       │       │        │
│  └────────────────────┘        ┌────────▼┐ ┌───▼────┐ ┌▼───────┐│
│                                   │ Code    │ │Security │ │Remedi- ││
│                                   │ Analysis│ │Vuln     │ │ation   ││
│                                   │ Agent   │ │Agent    │ │Agent   ││
│                                   └────┬────┘ └───┬─────┘ └───┬────┘│
│                                        └────┬──────┘           │    │
│                                        ┌────▼──────────────┐   │    │
│                                        │  PR Summary Agent  │◀──┘    │
│                                        └────┬──────────────┘        │
│                                             │                        │
│                              ┌──────────────▼─────────────────┐     │
│                              │ Conversational Code Assistant   │     │
│                              │ (RAG: retrieves from Chroma)    │     │
│                              └──────────────┬───────────────────┘   │
└─────────────────────────────────────────────┼───────────────────────┘
                                                │
                                    ┌───────────▼────────────┐
                                    │   ChromaDB Vector Store │
                                    │  (OWASP + secure coding │
                                    │   docs, chunked+embedded)│
                                    └──────────────────────────┘
```

**Orchestration flow for Milestone 1 (you're only building submission + KB, but design for the full flow now):**
1. User submits code → validated → stored as a `CodeSubmission` object
2. Orchestrator will eventually fan this out to the 3 analysis agents in parallel, then feed results to Remediation → PR Summary
3. Conversational Assistant queries the vector store independently, on-demand

---

## 2. Data Models (design deliverable #2)

```python
# models.py
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class Language(str, Enum):
    PYTHON = "python"
    JAVA = "java"

class SubmissionMethod(str, Enum):
    PASTE = "paste"
    UPLOAD = "upload"

class CodeSubmission(BaseModel):
    id: str
    language: Language
    method: SubmissionMethod
    raw_code: str
    filename: str | None = None
    submitted_at: datetime
    is_valid_syntax: bool
    syntax_errors: list[str] = []

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
    category: str              # e.g. "SQL Injection", "Code Smell: God Class"
    severity: Severity
    line_start: int
    line_end: int
    description: str
    remediation: str | None = None
    fixed_code_snippet: str | None = None

class KnowledgeChunk(BaseModel):
    id: str
    source_doc: str            # e.g. "OWASP Top 10 2021"
    text: str
    embedding: list[float]
    metadata: dict
```

Keep this file as your single source of truth — every agent should read/write these shapes so the pipeline doesn't drift.

---

## 3. Build Order for Milestone 1

### Step A — Research (Deliverable 1)
Spend 2–3 focused sessions on:
- **OWASP Top 10** (2021 list) — this is your Security Vulnerability Agent's checklist
- **OWASP Secure Coding Practices Quick Reference Guide** — feeds your knowledge base
- **Code smell catalogue** (long method, god class, duplicate code, feature envy, etc.) — feeds Code Analysis Agent
- **RAG architecture basics** — chunking strategies, embedding models, retrieval (top-k, similarity threshold), and how retrieved context gets injected into a prompt

Deliverable: a short internal notes doc (I can help you draft this once you've read the source material — paste your notes and I'll help structure them).

### Step B — Architecture & Data Models (Deliverable 2)
Use Section 1 and Section 2 above as your starting draft. Adjust based on what you learn in Step A, then lock it before writing code — changing data models mid-build is the most expensive kind of rework.

### Step C — Code Submission Module (Deliverable 3)

**Folder structure:**
```
backend/
  app/
    main.py
    models.py
    submission/
      __init__.py
      router.py          # FastAPI endpoints
      validator.py        # syntax validation logic
      service.py           # orchestrates paste/upload → CodeSubmission
```

**`validator.py` — syntax validation for both languages:**
```python
import ast
import javalang

def validate_python(code: str) -> tuple[bool, list[str]]:
    try:
        ast.parse(code)
        return True, []
    except SyntaxError as e:
        return False, [f"Line {e.lineno}: {e.msg}"]

def validate_java(code: str) -> tuple[bool, list[str]]:
    try:
        javalang.parse.parse(code)
        return True, []
    except javalang.parser.JavaSyntaxError as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"Parse error: {str(e)}"]

def validate(code: str, language: str) -> tuple[bool, list[str]]:
    if language == "python":
        return validate_python(code)
    elif language == "java":
        return validate_java(code)
    raise ValueError(f"Unsupported language: {language}")
```

**`router.py` — endpoints for paste + upload:**
```python
from fastapi import APIRouter, UploadFile, File, Form
from uuid import uuid4
from datetime import datetime
from ..models import CodeSubmission, Language, SubmissionMethod
from .validator import validate

router = APIRouter(prefix="/submission", tags=["submission"])

@router.post("/paste")
async def submit_pasted_code(code: str = Form(...), language: Language = Form(...)):
    is_valid, errors = validate(code, language.value)
    submission = CodeSubmission(
        id=str(uuid4()),
        language=language,
        method=SubmissionMethod.PASTE,
        raw_code=code,
        submitted_at=datetime.utcnow(),
        is_valid_syntax=is_valid,
        syntax_errors=errors,
    )
    # TODO: persist submission (in-memory dict for MVP, DB later)
    return submission

@router.post("/upload")
async def submit_uploaded_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    language = Language.PYTHON if file.filename.endswith(".py") else Language.JAVA
    is_valid, errors = validate(content, language.value)
    submission = CodeSubmission(
        id=str(uuid4()),
        language=language,
        method=SubmissionMethod.UPLOAD,
        raw_code=content,
        filename=file.filename,
        submitted_at=datetime.utcnow(),
        is_valid_syntax=is_valid,
        syntax_errors=errors,
    )
    return submission
```

**Frontend piece (Step C, React side):** a simple two-tab component — one `<textarea>` for paste, one drag-and-drop zone for `.py`/`.java` upload, both POSTing to the endpoints above and rendering `syntax_errors` inline if invalid. I can build this out fully with you when you're ready to wire up the UI — just say the word and I'll write the component.

**Setup commands:**
```bash
python -m venv venv
source venv/bin/activate       # or venv\Scripts\activate on Windows
pip install fastapi uvicorn python-multipart javalang astroid pydantic
uvicorn app.main:app --reload
```

### Step D — Secure Coding Knowledge Base + RAG Pipeline (Deliverable 4)

**Folder structure:**
```
backend/
  app/
    knowledge_base/
      __init__.py
      ingest.py           # chunk + embed + store documents
      retriever.py        # query the vector store
    data/
      raw_docs/            # OWASP PDFs/markdown you've collected
```

**`ingest.py` — chunking, embedding, indexing:**
```python
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import uuid

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection("secure_coding_kb")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def ingest_document(filepath: str, source_name: str):
    text = Path(filepath).read_text(encoding="utf-8")
    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": source_name, "chunk_index": i} for i in range(len(chunks))]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    print(f"Ingested {len(chunks)} chunks from {source_name}")

if __name__ == "__main__":
    ingest_document("data/raw_docs/owasp_top_10.md", "OWASP Top 10 2021")
    ingest_document("data/raw_docs/secure_coding_qrg.md", "OWASP Secure Coding QRG")
```

**`retriever.py` — query interface the Conversational Assistant will call later:**
```python
from .ingest import model, collection

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]
```

**Setup commands:**
```bash
pip install chromadb sentence-transformers
```

**Where to get source documents for the KB:**
- OWASP Top 10 (owasp.org — download or copy into markdown)
- OWASP Secure Coding Practices Quick Reference Guide
- OWASP Cheat Sheet Series (pick the ones relevant to your OWASP categories: SQLi, XSS, Auth, Access Control)

Save each as a `.md` or `.txt` in `data/raw_docs/` before running `ingest.py`.

---

## 4. Milestone 1 Checklist

- [ ] Research notes on OWASP, code smells, RAG (Step A)
- [ ] Architecture diagram + data models locked in (Step B)
- [ ] `validate.py` working for both Python and Java, tested with intentionally broken code
- [ ] `/submission/paste` and `/submission/upload` endpoints returning correct `CodeSubmission` objects
- [ ] Frontend paste/upload UI wired to backend
- [ ] At least 3–4 OWASP source documents collected and saved locally
- [ ] `ingest.py` run successfully, chunks visible in ChromaDB
- [ ] `retriever.py` returns relevant chunks for a test query (e.g., "how do I prevent SQL injection")

---

## Next Steps
Once you're ready to start coding, tell me which piece you want to build first — I'd suggest starting with the Code Submission Module since it's self-contained and testable in isolation, then moving to the Knowledge Base. I can write out full working code for each file above, help debug, or extend into Milestone 2's agent logic whenever you're ready.
