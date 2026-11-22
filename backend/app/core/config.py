import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ENV_FILE = _BACKEND_DIR / ".env"

class Settings(BaseSettings):
    # LLM Settings
    groq_api_key: str = "your_groq_api_key_here"
    model_name: str = "qwen/qwen3.8-27b"
    hf_api_key: str = ""

    # Neo4j Settings
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"

    # Relational Database Settings
    database_url: str = f"sqlite:///{_BACKEND_DIR / 'math_learning.db'}"

    # Vector Store & Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = str(_BACKEND_DIR / "vector_store")
    data_path: str = str(_BACKEND_DIR / "data")
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5

    class Config:
        env_file = str(_ENV_FILE)
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
