import pytest
from backend.app.services.rag.retriever import retrieve_context, get_vectorstore, format_context_for_prompt
from backend.app.services.rag.ingest import clean_text, extract_concepts_from_text

def test_clean_text():
    raw = "  Calculus   \n\n\n\n  is great  "
    cleaned = clean_text(raw)
    assert cleaned == "Calculus\n\nis great"

def test_extract_concepts():
    text = "We study Limits, Continuity, and Differentiation before Integration."
    concepts = extract_concepts_from_text(text)
    assert "Limits" in concepts
    assert "Differentiation" in concepts
    assert "Integration" in concepts

def test_vectorstore_initialization():
    vs = get_vectorstore()
    assert vs is not None

def test_similarity_search():
    results = retrieve_context("What is differentiation and derivative rules?", top_k=2)
    assert len(results) > 0
    formatted = format_context_for_prompt(results)
    assert "Calculus" in formatted or "Differentiation" in formatted
