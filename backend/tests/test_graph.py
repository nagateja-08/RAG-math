import pytest
from backend.app.services.graph.graph_service import get_graph_service

def test_graph_initialization():
    service = get_graph_service()
    status = service.get_status()
    assert status["total_nodes"] > 20
    assert status["mode"] in ("live_neo4j", "in_memory_resilient_store")

def test_find_concept():
    service = get_graph_service()
    calc = service.find_concept("Integration")
    assert calc is not None
    assert calc["name"] == "Integration"
    assert calc["subject"] == "Calculus"

def test_concept_neighborhood():
    service = get_graph_service()
    data = service.get_concept_neighborhood("Integration")
    assert data["concept"] == "Integration"
    assert "Differentiation" in data["prerequisites"] or "Limits" in data["prerequisites"]
    assert len(data["formulas"]) > 0

def test_prerequisite_traversal():
    service = get_graph_service()
    res = service.get_prerequisites_chain("Integration")
    assert res["target_concept"] == "Integration"
    assert len(res["direct_prerequisites"]) > 0
    assert "Differentiation" in res["direct_prerequisites"] or "Limits" in res["direct_prerequisites"]

def test_dynamic_node_addition():
    service = get_graph_service()
    res = service.add_concept_dynamically(
        name="Fourier Transform",
        subject="Calculus",
        difficulty="Advanced",
        description="Decomposes a function into frequency components",
        source="Unit Test",
        prerequisites=["Integration"]
    )
    assert res["status"] in ("created", "exists")
    found = service.find_concept("Fourier Transform")
    assert found is not None
    assert found["name"] == "Fourier Transform"
