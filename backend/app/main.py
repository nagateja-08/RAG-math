import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .core.config import get_settings
from .services.rag.retriever import get_vectorstore
from .services.graph.graph_service import get_graph_service

# Import API Routers
from .api.v1.ask import router as ask_router
from .api.v1.chat import router as chat_router
from .api.v1.graph import router as graph_router
from .api.v1.prerequisites import router as prereq_router
from .api.v1.verify import router as verify_router
from .api.v1.assessment import router as assessment_router
from .api.v1.progress import router as progress_router
from .api.v1.upload import router as upload_router
from .api.v1.health import router as health_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mathgpt.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Bootstrap databases, vector store, and knowledge graph on startup."""
    logger.info("Initializing MathGPT Intelligent Mathematical Learning Platform...")
    try:
        init_db()
        logger.info("Relational database initialized for student learning analytics.")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

    try:
        get_graph_service()
        logger.info("Mathematical Knowledge Graph service initialized.")
    except Exception as e:
        logger.warning(f"Knowledge Graph initialization warning: {e}")

    try:
        get_vectorstore()
        logger.info("FAISS vector store and embedding models initialized.")
    except Exception as e:
        logger.warning(f"FAISS initialization warning: {e}")

    logger.info("MathGPT Platform is fully operational and ready!")
    yield

app = FastAPI(
    title="MathGPT API",
    description="Graph-Enhanced RAG-Based Intelligent Mathematical Learning Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api/v1
app.include_router(ask_router, prefix="/api/v1", tags=["RAG & Graph Ask"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(graph_router, prefix="/api/v1", tags=["Knowledge Graph"])
app.include_router(prereq_router, prefix="/api/v1", tags=["Prerequisites"])
app.include_router(verify_router, prefix="/api/v1", tags=["SymPy Verification"])
app.include_router(assessment_router, prefix="/api/v1", tags=["Assessments"])
app.include_router(progress_router, prefix="/api/v1", tags=["Learning Analytics"])
app.include_router(upload_router, prefix="/api/v1", tags=["Document Ingestion"])
app.include_router(health_router, prefix="/api/v1", tags=["Health"])

# Direct top-level route aliases matching Section 7 specifications
app.include_router(ask_router, tags=["Direct Aliases"])
app.include_router(graph_router, tags=["Direct Aliases"])
app.include_router(prereq_router, tags=["Direct Aliases"])
app.include_router(verify_router, tags=["Direct Aliases"])
app.include_router(assessment_router, tags=["Direct Aliases"])
app.include_router(progress_router, tags=["Direct Aliases"])
app.include_router(upload_router, tags=["Direct Aliases"])

@app.get("/")
def read_root():
    return {
        "platform": "MathGPT - Graph-Enhanced RAG Intelligent Mathematical Learning Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "ask": "/api/v1/ask",
            "graph": "/api/v1/graph",
            "prerequisites": "/api/v1/prerequisites/{concept}",
            "verify": "/api/v1/verify",
            "assessment": "/api/v1/assessment/{concept}",
            "progress": "/api/v1/progress",
            "upload": "/api/v1/upload"
        }
    }
