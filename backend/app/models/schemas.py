from pydantic import BaseModel
from typing import Optional, List


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    use_rag: Optional[bool] = True
    use_sympy: Optional[bool] = False
    sympy_tool: Optional[str] = None
    sympy_args: Optional[dict] = {}
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    answer: str
    context_used: Optional[List[str]] = []
    sympy_result: Optional[dict] = None
    model: str


class UploadResponse(BaseModel):
    filename: str
    message: str
    chunks_added: int


class HealthResponse(BaseModel):
    status: str
    model: str
    vector_store_loaded: bool
