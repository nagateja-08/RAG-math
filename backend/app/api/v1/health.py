from fastapi import APIRouter
from ...core.config import get_settings
from ...models.schemas import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check — returns service status, model name, and vector store state."""
    vector_store_loaded = False
    try:
        from ...services.rag.retriever import get_vectorstore
        get_vectorstore()
        vector_store_loaded = True
    except Exception:
        vector_store_loaded = False

    return HealthResponse(
        status="ok",
        model=settings.model_name,
        vector_store_loaded=vector_store_loaded,
    )
