from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...services.graph.graph_service import get_graph_service
from ...models.schemas import GraphDataResponse, TopicsResponse

router = APIRouter()

@router.get("/graph", response_model=GraphDataResponse)
def get_graph(subject: Optional[str] = Query(None, description="Filter graph nodes by subject (Calculus, Algebra, etc.)")):
    """Retrieve graph nodes and relationships for the Interactive Knowledge Graph Explorer (Feature 1)."""
    service = get_graph_service()
    return service.get_entire_graph(subject=subject)

@router.get("/graph/{concept}")
def get_concept_details(concept: str):
    """Retrieve detailed relationships, formulas, theorems, and prerequisites for a concept node."""
    service = get_graph_service()
    data = service.get_concept_neighborhood(concept)
    if not data or not data.get("concept"):
        raise HTTPException(status_code=404, detail=f"Concept '{concept}' not found in Knowledge Graph.")
    return data

@router.get("/topics", response_model=TopicsResponse)
def get_topics():
    """List available mathematical topics organized by subject."""
    service = get_graph_service()
    return service.get_topics_and_subjects()
