from fastapi import APIRouter, HTTPException
from ...services.graph.graph_service import get_graph_service
from ...models.schemas import PrerequisiteTreeResponse

router = APIRouter()

@router.get("/prerequisites/{concept}", response_model=PrerequisiteTreeResponse)
def get_prerequisites(concept: str):
    """
    Retrieve prerequisite concepts and dependency paths using Neo4j graph traversal (Feature 2).
    """
    service = get_graph_service()
    data = service.get_prerequisites_chain(concept)
    if not data:
        raise HTTPException(status_code=404, detail=f"No prerequisite data found for '{concept}'.")
    return data
