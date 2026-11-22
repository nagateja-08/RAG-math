from fastapi import APIRouter
from ...core.config import get_settings
from ...models.schemas import HealthResponse
from ...services.graph.graph_service import get_graph_service
from ...services.rag.retriever import get_vectorstore
from ...services.llm.groq_client import get_groq_client

router = APIRouter()
settings = get_settings()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """System health check endpoint."""
    llm_connected = (get_groq_client() is not None)

    vector_store_loaded = False
    try:
        vs = get_vectorstore()
        vector_store_loaded = (vs is not None)
    except Exception:
        vector_store_loaded = False

    graph_service = get_graph_service()
    graph_status = graph_service.get_status()

    return HealthResponse(
        status="healthy",
        llm_connected=llm_connected,
        vector_store_loaded=vector_store_loaded,
        neo4j_connected=graph_status["is_live"],
        neo4j_mode=graph_status["mode"],
        total_graph_nodes=graph_status["total_nodes"],
        model_name=settings.model_name
    )
