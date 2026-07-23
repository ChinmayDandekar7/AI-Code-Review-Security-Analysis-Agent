"""
Query interface into the secure coding knowledge base.
"""

from pathlib import Path

import chromadb

from .embeddings import get_embedding_function

CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_store"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection(
    "secure_coding_kb",
    embedding_function=get_embedding_function(),
)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[query], n_results=top_k)

    return [
        {"text": doc, "source": meta["source"], "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "how do I prevent sql injection"
    print(f"Query: {query}\n")
    for i, r in enumerate(retrieve(query), start=1):
        print(f"--- Result {i} (source: {r['source']}, distance: {r['distance']:.4f}) ---")
        print(r["text"][:300])
        print()
