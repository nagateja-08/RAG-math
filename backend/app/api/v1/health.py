from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check returning service status."""
    return {"status": "ok", "service": "MathGPT API"}
