"""
Ingest secure-coding source documents into the ChromaDB vector store.

Pipeline: read doc -> chunk -> embed -> store, with metadata so retrieved
chunks can always be traced back to their source document.

Usage:
    python -m app.knowledge_base.ingest
"""

import uuid
from pathlib import Path

import chromadb

from .embeddings import get_embedding_function

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw_docs"
CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_store"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection(
    "secure_coding_kb",
    embedding_function=get_embedding_function(),
)


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """
    Simple word-count based chunking with overlap, so retrieved context
    isn't cut off mid-idea at chunk boundaries.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
        i += chunk_size - overlap
    return chunks


def ingest_document(filepath: Path, source_name: str) -> int:
    text = filepath.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    if not chunks:
        print(f"Skipped {source_name} (no content)")
        return 0

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {"source": source_name, "chunk_index": i, "filename": filepath.name}
        for i in range(len(chunks))
    ]

    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    print(f"Ingested {len(chunks)} chunks from {source_name}")
    return len(chunks)


def ingest_all():
    if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
        print(f"No documents found in {DATA_DIR}. Add .md/.txt files there first.")
        return

    total = 0
    for filepath in sorted(DATA_DIR.glob("*")):
        if filepath.suffix.lower() in (".md", ".txt"):
            source_name = filepath.stem.replace("_", " ").title()
            total += ingest_document(filepath, source_name)

    print(f"\nDone. {total} total chunks in collection '{collection.name}'.")
    print(f"Collection count: {collection.count()}")


if __name__ == "__main__":
    ingest_all()
