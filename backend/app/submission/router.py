"""
API endpoints for the Code Submission Module.

Two entry points, matching the project brief exactly:
  - POST /submission/paste   -> paste code directly
  - POST /submission/upload  -> upload a .py or .java file

For Milestone 1, submissions are kept in an in-memory dict. This is fine
for local dev/testing; swap for a real database once you need submissions
to persist across restarts.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from uuid import uuid4
from datetime import datetime

from ..models import CodeSubmission, Language, SubmissionMethod
from .validator import validate
from .language_detector import detect_language

router = APIRouter(prefix="/submission", tags=["submission"])

# In-memory store — Milestone 1 only. Replace with a DB later.
SUBMISSIONS: dict[str, CodeSubmission] = {}


@router.post("/paste", response_model=CodeSubmission)
async def submit_pasted_code(code: str = Form(...), language: Language | None = Form(None)):
    if not code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    # Auto-detect language from the code itself unless the caller explicitly
    # overrides it (e.g. a future "force language" UI control).
    resolved_language = language or Language(detect_language(code))

    is_valid, errors = validate(code, resolved_language.value)
    submission = CodeSubmission(
        id=str(uuid4()),
        language=resolved_language,
        method=SubmissionMethod.PASTE,
        raw_code=code,
        submitted_at=datetime.utcnow(),
        is_valid_syntax=is_valid,
        syntax_errors=errors,
    )
    SUBMISSIONS[submission.id] = submission
    return submission


@router.post("/upload", response_model=CodeSubmission)
async def submit_uploaded_file(file: UploadFile = File(...)):
    if not (file.filename.endswith(".py") or file.filename.endswith(".java")):
        raise HTTPException(
            status_code=400,
            detail="Only .py and .java files are supported.",
        )

    raw_bytes = await file.read()
    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text.")

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
    SUBMISSIONS[submission.id] = submission
    return submission


@router.post("/detect-language")
async def detect_language_endpoint(code: str = Form(...)):
    if not code.strip():
        return {"language": None}
    return {"language": detect_language(code)}


@router.get("/{submission_id}", response_model=CodeSubmission)
async def get_submission(submission_id: str):
    submission = SUBMISSIONS.get(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission
