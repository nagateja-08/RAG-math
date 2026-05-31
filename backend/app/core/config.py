from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# Resolve paths relative to this config file (backend/app/core/config.py)
# so they work correctly regardless of where uvicorn is launched from.
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # backend/
_ENV_FILE = _BACKEND_DIR / ".env"

class Settings(BaseSettings):
    groq_api_key: str = "your_groq_api_key_here"
    hf_api_key: str = ""
    model_name: str = "llama-3.3-70b-versatile"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_store_path: str = str(_BACKEND_DIR / "vector_store")
    data_path: str = str(_BACKEND_DIR / "data")
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5

    class Config:
        env_file = str(_ENV_FILE)

@lru_cache()
def get_settings():
    return Settings()
