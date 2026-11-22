import pytest
from backend.app.api.v1.health import health_check
from backend.app.api.v1.graph import get_graph, get_topics, get_concept_details
from backend.app.api.v1.prerequisites import get_prerequisites
from backend.app.api.v1.verify import verify_math_expression
from backend.app.api.v1.assessment import get_quiz
from backend.app.api.v1.progress import get_progress
from backend.app.models.schemas import VerifyRequest
from backend.app.core.database import SessionLocal, init_db

def test_health_endpoint():
    res = health_check()
    assert res.status == "healthy"
    assert res.total_graph_nodes > 10
    assert res.neo4j_mode in ("live_neo4j", "in_memory_resilient_store")

def test_graph_endpoint():
    res = get_graph(subject=None)
    assert len(res.nodes) > 15
    assert len(res.edges) > 10
    assert res.total_nodes == len(res.nodes)

def test_concept_details_endpoint():
    res = get_concept_details("Integration")
    assert res["concept"] == "Integration"
    assert "Differentiation" in res["prerequisites"] or "Limits" in res["prerequisites"]

def test_topics_endpoint():
    res = get_topics()
    assert "Calculus" in res["subjects"]
    assert "Algebra" in res["subjects"]
    assert "Integration" in res["topics_by_subject"]["Calculus"]

def test_prerequisites_endpoint():
    res = get_prerequisites("Integration")
    assert res["target_concept"] == "Integration"
    assert len(res["direct_prerequisites"]) > 0

def test_verify_endpoint():
    req = VerifyRequest(expression="x^2 - 4 = 0", operation="solve", variable="x")
    res = verify_math_expression(req)
    assert res.success is True
    assert res.verified is True
    assert "2" in res.symbolic_result

def test_assessment_endpoint():
    res = get_quiz("Integration")
    assert res.target_concept == "Integration"
    assert len(res.questions) > 0

def test_progress_endpoint():
    init_db()
    db = SessionLocal()
    try:
        res = get_progress(user_id="test_student", db=db)
        assert res["user_id"] == "test_student"
        assert isinstance(res["recommended_study_plan"], list)
    finally:
        db.close()
