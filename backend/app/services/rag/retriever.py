"""
FAISS Retriever for MathGPT RAG Pipeline
Loads the pre-built FAISS index and performs semantic search.
Uses a local HuggingFace embedding model (all-MiniLM-L6-v2) - fast and free.
"""

import os
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ...core.config import get_settings

settings = get_settings()

# Singletons - both pre-loaded once at startup
_embeddings = None
_vectorstore = None


def get_embeddings():
    """Return the singleton HuggingFace embedding model (loaded once)."""
    global _embeddings
    if _embeddings is None:
        print(f"[INFO] Loading embedding model: {settings.embedding_model}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("[SUCCESS] Embedding model loaded.")
    return _embeddings


def get_vectorstore():
    """Lazy-load the FAISS vectorstore (singleton)."""
    global _vectorstore
    if _vectorstore is None:
        index_path = settings.vector_store_path
        if not Path(index_path).exists():
            raise FileNotFoundError(
                f"FAISS index not found at '{index_path}'. "
                "Please run: python -m app.services.rag.ingest"
            )

        print(f"[INFO] Loading FAISS index from: {index_path}")
        embeddings = get_embeddings()
        _vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("[SUCCESS] FAISS index loaded successfully.")
    return _vectorstore


def retrieve_context(query: str, top_k: int = None) -> list[str]:
    """
    Retrieve top-K relevant math Q&A chunks for a given query.
    Returns a list of text strings.
    """
    if top_k is None:
        top_k = settings.top_k_results

    try:
        vs = get_vectorstore()
        results = vs.similarity_search(query, k=top_k)
        return [doc.page_content for doc in results]
    except FileNotFoundError as e:
        print(f"[WARN] Vector store not available: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Retrieval error: {e}")
        return []


def format_context(chunks: list[str]) -> str:
    """Format retrieved chunks into a single context string."""
    if not chunks:
        return ""
    formatted = "\n\n---\n\n".join(
        [f"[Reference {i+1}]\n{chunk}" for i, chunk in enumerate(chunks)]
    )
    return formatted
