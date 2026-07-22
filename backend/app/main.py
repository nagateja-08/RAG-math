from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.chat import router as chat_router
from .api.v1.upload import router as upload_router
from .api.v1.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the embedding model and FAISS index at startup."""
    print("[STARTUP] Pre-loading embedding model and FAISS index...")
    try:
        from .services.rag.retriever import get_vectorstore
        get_vectorstore()  # loads embeddings + FAISS index into memory
        print("[STARTUP] Ready! All models loaded.")
    except Exception as e:
        print(f"[STARTUP WARN] Could not pre-load: {e}")
    yield


app = FastAPI(
    title="MathGPT API",
    description="Production-ready Mathematical AI Assistant Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - allow frontend (React) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin (including Vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])


@app.get("/")
def read_root():
    return {
        "name": "MathGPT API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
