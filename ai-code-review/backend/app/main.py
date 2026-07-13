"""
App entrypoint. Run with:
    uvicorn app.main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive API testing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .submission.router import router as submission_router
from .knowledge_base.router import router as knowledge_router

app = FastAPI(
    title="AI Code Review & Security Analysis Agent",
    description="Milestone 1: Code Submission Module + Secure Coding Knowledge Base",
    version="0.1.0",
)

# Allow the local React dev server to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submission_router)
app.include_router(knowledge_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "ai-code-review-backend"}
