"""
Embedding function used by both ingest.py and retriever.py.

Production (your machine, full internet): sentence-transformers pulls
'all-MiniLM-L6-v2' from Hugging Face on first run, then caches it locally.

Sandbox note: this dev environment can't reach huggingface.co, so if that
import/download fails, this falls back to a deterministic offline hashing
embedder purely so the pipeline can be tested end to end here. On your
machine, EMBEDDING_MODE defaults to "sentence_transformers" and the
hashing fallback is never used.
"""

import os
import re
import hashlib
import numpy as np
from chromadb import EmbeddingFunction, Documents, Embeddings

EMBEDDING_MODE = os.environ.get("EMBEDDING_MODE", "sentence_transformers")
HASH_DIM = 384


class HashingEmbeddingFunction(EmbeddingFunction):
    """Deterministic, dependency-free embedding for offline testing only."""

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed_one(text) for text in input]

    def _embed_one(self, text: str) -> list[float]:
        vec = np.zeros(HASH_DIM, dtype=np.float32)
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for tok in tokens:
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            idx = h % HASH_DIM
            sign = 1.0 if (h // HASH_DIM) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def name() -> str:
        return "hashing_embedding_offline_test"

    def get_config(self) -> dict:
        return {}

    @staticmethod
    def build_from_config(config: dict) -> "HashingEmbeddingFunction":
        return HashingEmbeddingFunction()


def get_embedding_function():
    if EMBEDDING_MODE == "sentence_transformers":
        try:
            from chromadb.utils.embedding_functions import (
                SentenceTransformerEmbeddingFunction,
            )

            return SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        except Exception as e:
            print(f"[embeddings] sentence-transformers unavailable ({e}); "
                  f"falling back to the offline hashing embedder.")

    print("[embeddings] Using offline hashing embedder (testing only). Set "
          "EMBEDDING_MODE=sentence_transformers on a machine with internet "
          "access for real embeddings.")
    return HashingEmbeddingFunction()
