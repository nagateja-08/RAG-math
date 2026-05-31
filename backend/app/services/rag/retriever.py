"""
FAISS Retriever for MathGPT RAG Pipeline
Loads the pre-built FAISS index and performs semantic search.
Uses HuggingFace Inference API for embeddings to minimize memory usage.
"""

import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from ...core.config import get_settings

settings = get_settings()
_vectorstore = None


def _get_embeddings():
    """Create HuggingFace Inference API embeddings (no local model needed)."""
    return HuggingFaceInferenceAPIEmbeddings(
        api_key=settings.hf_api_key,
        model_name=f"sentence-transformers/{settings.embedding_model}",
    )


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
        embeddings = _get_embeddings()
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
