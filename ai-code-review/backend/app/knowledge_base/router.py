"""
HTTP interface to the secure coding knowledge base retriever.
Wraps the already-tested retriever.retrieve() function from Milestone 1
deliverable 3 so the frontend (and later, the Conversational Assistant
agent) can query it over the API instead of only via CLI.
"""

from fastapi import APIRouter, HTTPException, Query

from .retriever import retrieve

router = APIRouter(prefix="/knowledge", tags=["knowledge_base"])


@router.get("/search")
async def search_knowledge_base(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(5, ge=1, le=20),
):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    results = retrieve(q, top_k=top_k)
    return {"query": q, "results": results}
