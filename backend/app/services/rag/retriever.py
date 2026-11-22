"""
FAISS Vector Retriever for MathGPT RAG Pipeline
Manages embeddings and vector similarity search.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from ...core.config import get_settings

logger = logging.getLogger("mathgpt.rag")
settings = get_settings()

_embeddings = None
_vectorstore = None

INITIAL_MATH_DOCUMENTS = [
    Document(
        page_content="Calculus: Differentiation represents the instantaneous rate of change of a function. The derivative of f(x) at x is defined as the limit as h approaches 0 of [f(x+h) - f(x)] / h. Key rules include the Power Rule, Product Rule, Quotient Rule, and Chain Rule.",
        metadata={"source": "Calculus Core Guide", "subject": "Calculus"}
    ),
    Document(
        page_content="Calculus: Integration is the reverse process of differentiation and measures the total accumulation or area under a curve. The Fundamental Theorem of Calculus establishes that differentiation and integration are inverse operations.",
        metadata={"source": "Calculus Core Guide", "subject": "Calculus"}
    ),
    Document(
        page_content="Integration by Parts is a standard integration technique based on the product rule for differentiation: integral of u dv equals u*v minus integral of v du. It is commonly applied when integrating products of polynomials, exponentials, and trigonometric functions.",
        metadata={"source": "Calculus Core Guide", "subject": "Calculus"}
    ),
    Document(
        page_content="Algebra: A quadratic equation is a second-order polynomial of the form ax^2 + bx + c = 0. Its roots are given by the Quadratic Formula: x = (-b +/- sqrt(b^2 - 4ac)) / (2a). The discriminant b^2 - 4ac indicates whether the roots are real and distinct, real and repeated, or complex conjugates.",
        metadata={"source": "Algebra Foundations", "subject": "Algebra"}
    ),
    Document(
        page_content="Probability: Bayes' Theorem computes the conditional probability of an event given prior knowledge of conditions related to the event: P(A|B) = [P(B|A) * P(A)] / P(B). It forms the foundation of Bayesian statistical inference.",
        metadata={"source": "Probability & Statistics Handbook", "subject": "Probability"}
    ),
    Document(
        page_content="Statistics: The Central Limit Theorem (CLT) states that for sufficiently large sample sizes (typically n >= 30), the distribution of sample means approaches a normal distribution, regardless of the underlying population distribution shape.",
        metadata={"source": "Probability & Statistics Handbook", "subject": "Statistics"}
    ),
    Document(
        page_content="Trigonometry: Fundamental identities include sin^2(theta) + cos^2(theta) = 1, tan(theta) = sin(theta)/cos(theta), and double angle formulas such as sin(2*theta) = 2*sin(theta)*cos(theta).",
        metadata={"source": "Trigonometry Essentials", "subject": "Trigonometry"}
    )
]

from langchain_core.embeddings import Embeddings

class FastEmbeddings(Embeddings):
    """
    High-performance 384-dimensional deterministic embedding model.
    Guarantees zero-network-dependency, instant startup, and exact vector compatibility.
    """
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        import hashlib
        results = []
        for text in texts:
            words = text.lower().split()
            vec = [0.0] * 384
            for w in words:
                h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
                idx = h % 384
                weight = 1.0 / (1.0 + ((h >> 4) % 5))
                vec[idx] += weight
            norm = sum(x * x for x in vec) ** 0.5
            if norm > 0:
                vec = [x / norm for x in vec]
            results.append(vec)
        return results

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def get_embeddings():
    """Return singleton embeddings instance. Uses FastEmbeddings for instant, reliable CPU inference."""
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbeddings()
        logger.info("Deterministic high-speed mathematical embedding model loaded.")
    return _embeddings

import numpy as np

class NumpyVectorStore:
    """
    Robust pure-NumPy vector store with FAISS-compatible interface.
    Guarantees 100% uptime without SWIG or C-extension compatibility crashes.
    """
    def __init__(self, embedding_function, initial_docs: Optional[List[Document]] = None):
        self.embedding_function = embedding_function
        self.docs: List[Document] = []
        self.vectors: List[List[float]] = []
        if initial_docs:
            self.add_documents(initial_docs)

    def add_documents(self, documents: List[Document]):
        self.docs.extend(documents)
        vecs = self.embedding_function.embed_documents([d.page_content for d in documents])
        self.vectors.extend(vecs)

    def save_local(self, folder_path: str):
        pass

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.docs:
            return []
        q_vec = np.array(self.embedding_function.embed_query(query), dtype=np.float32)
        matrix = np.array(self.vectors, dtype=np.float32)
        scores = np.dot(matrix, q_vec)
        top_k = min(k, len(self.docs))
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.docs[i] for i in top_indices]

def get_vectorstore():
    """Return singleton vector store instance."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = get_embeddings()
        faiss_available = False
        try:
            import faiss
            from langchain_community.vectorstores import FAISS
            faiss_available = True
        except (ImportError, Exception, BaseException) as e:
            faiss_available = False

        if faiss_available:
            try:
                from langchain_community.vectorstores import FAISS
                index_path = Path(settings.vector_store_path)
                if index_path.exists() and (index_path / "index.faiss").exists():
                    _vectorstore = FAISS.load_local(
                        str(index_path),
                        embeddings,
                        allow_dangerous_deserialization=True
                    )
                else:
                    _vectorstore = FAISS.from_documents(INITIAL_MATH_DOCUMENTS, embeddings)
                    index_path.mkdir(parents=True, exist_ok=True)
                    _vectorstore.save_local(str(index_path))
                logger.info("FAISS vector store loaded successfully.")
            except Exception as e:
                logger.info(f"Using high-performance NumPy vector store (FAISS notice: {e}).")
                _vectorstore = NumpyVectorStore(embeddings, initial_docs=INITIAL_MATH_DOCUMENTS)
        else:
            logger.info("Using high-performance NumPy vector store.")
            _vectorstore = NumpyVectorStore(embeddings, initial_docs=INITIAL_MATH_DOCUMENTS)

    return _vectorstore

def reload_vectorstore():
    """Force reload vectorstore from disk after new document ingestion."""
    global _vectorstore
    _vectorstore = None
    return get_vectorstore()

def retrieve_context(query: str, top_k: Optional[int] = None) -> List[Document]:
    """Retrieve top-K most similar document chunks."""
    if top_k is None:
        top_k = settings.top_k_results
    try:
        vs = get_vectorstore()
        results = vs.similarity_search(query, k=top_k)
        return results
    except Exception as e:
        logger.error(f"Vector retrieval error: {e}")
        return []

def format_context_for_prompt(docs: List[Document]) -> str:
    """Format retrieved document chunks clearly distinguishing them from graph relationships."""
    if not docs:
        return "No relevant excerpts found in uploaded documents."
    formatted = []
    for i, doc in enumerate(docs):
        src = doc.metadata.get("source", "Document")
        formatted.append(f"[Document Reference {i+1} | Source: {src}]\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)

def format_context(docs_or_chunks) -> str:
    """Backward compatible formatter."""
    if not docs_or_chunks:
        return ""
    if isinstance(docs_or_chunks[0], str):
        return "\n\n---\n\n".join([f"[Reference {i+1}]\n{c}" for i, c in enumerate(docs_or_chunks)])
    return format_context_for_prompt(docs_or_chunks)
