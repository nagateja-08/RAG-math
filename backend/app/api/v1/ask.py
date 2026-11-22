from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.schemas import AskRequest, AskResponse
from ...services.llm.orchestrator import execute_combined_pipeline

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Core Combined Graph-Enhanced RAG Endpoint (Section 4):
    1. Understands question & extracts mathematical concept
    2. Performs FAISS vector similarity search
    3. Retrieves Neo4j concept node, formulas, theorems, and prerequisites
    4. Combines context into LangChain prompt
    5. Calls Groq LLM for step-by-step mathematical reasoning
    6. Uses SymPy to independently verify calculations
    7. Updates student progress in database
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = execute_combined_pipeline(request, db=db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing combined RAG pipeline: {str(e)}")
