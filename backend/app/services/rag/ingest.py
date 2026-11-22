import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ...core.config import get_settings
from .retriever import get_embeddings, get_vectorstore, reload_vectorstore
from ..graph.graph_service import get_graph_service

settings = get_settings()

def clean_text(text: str) -> str:
    """Clean and normalize extracted mathematical text."""
    if not text:
        return ""
    # Normalize unicode spaces and dashes
    text = re.sub(r'[\r\f\v]', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(str(file_path))
    pages_text = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            pages_text.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(pages_text)

def extract_text_from_txt(file_path: Path) -> str:
    """Extract text from a plain TXT file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_concepts_from_text(text: str) -> List[str]:
    """
    Extract key mathematical concepts mentioned in text for Knowledge Graph synchronization.
    Extracts capitalized mathematical terms and known math entities.
    """
    known_math_terms = [
        "Limits", "Functions", "Differentiation", "Derivative", "Integration", "Integral",
        "Continuity", "Chain Rule", "Product Rule", "Integration by Parts",
        "Quadratic Equation", "Linear Equation", "Matrix", "Determinant", "Eigenvalue",
        "Trigonometry", "Sine", "Cosine", "Tangent", "Pythagorean Identity",
        "Probability", "Bayes Theorem", "Conditional Probability", "Random Variable",
        "Statistics", "Mean", "Standard Deviation", "Normal Distribution", "Hypothesis Testing"
    ]
    found = []
    text_lower = text.lower()
    for term in known_math_terms:
        if term.lower() in text_lower:
            found.append(term)
    return list(set(found))

def process_and_index_document(file_path: Path, original_filename: str) -> Tuple[int, List[str]]:
    """
    Full pipeline:
    1. Extract text from PDF / TXT
    2. Clean text
    3. Split into meaningful chunks
    4. Generate embeddings and add to FAISS
    5. Sync extracted concepts to Mathematical Knowledge Graph (Neo4j)
    """
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext in (".txt", ".md"):
        raw_text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF and TXT documents are supported.")

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise ValueError(f"No readable text could be extracted from {original_filename}.")

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", r"(?<=\.)\s+", " ", ""]
    )
    chunks = splitter.split_text(cleaned)

    docs = [
        Document(
            page_content=chunk,
            metadata={"source": original_filename, "chunk_id": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    # FAISS Ingestion
    embeddings = get_embeddings()
    index_path = Path(settings.vector_store_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        vs = get_vectorstore()
        vs.add_documents(docs)
        vs.save_local(str(index_path))
    except Exception:
        # Create new vector store if none exists
        vs = FAISS.from_documents(docs, embeddings)
        vs.save_local(str(index_path))

    reload_vectorstore()

    # Knowledge Graph Dynamic Sync
    extracted_concepts = extract_concepts_from_text(cleaned)
    graph_service = get_graph_service()
    for concept in extracted_concepts:
        graph_service.add_concept_dynamically(
            name=concept,
            subject="Uploaded Content",
            difficulty="Intermediate",
            description=f"Concept mentioned in uploaded document: {original_filename}",
            source=original_filename
        )

    return len(docs), extracted_concepts
