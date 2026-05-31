from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.chat import router as chat_router
from .api.v1.upload import router as upload_router
from .api.v1.health import router as health_router

app = FastAPI(
    title="MathGPT API",
    description="Production-ready Mathematical AI Assistant Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - allow frontend (React) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://localhost:5174"],
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
