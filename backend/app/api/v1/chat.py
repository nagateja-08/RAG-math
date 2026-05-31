import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, List, Dict

from ...models.schemas import ChatRequest
from ...core.config import get_settings
from ...services.rag.retriever import retrieve_context, format_context
from ...services.llm.groq_client import stream_chat
from ...services.math_engine.sympy_tools import process_sympy_blocks

settings = get_settings()

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict:
    """Handle a user query, retrieve relevant chunks, and return a JSON response."""
    if not request.message:
        raise HTTPException(status_code=400, detail="No message provided")

    user_msg_lower = request.message.lower()
    wrong_phrases = ["answer is wrong", "wrong answer", "you are wrong", "this is wrong", "incorrect answer", "incorrect"]
    if any(phrase in user_msg_lower for phrase in wrong_phrases):
        return {
            "answer": "We will check it and analyse now.",
            "context_used": [],
            "sympy_result": None,
            "model": settings.model_name,
        }

    # Retrieve context for the current message
    user_msg = request.message
    context_chunks = retrieve_context(user_msg)
    context = format_context(context_chunks)

    system_prompt = (
        "You are MathGPT — a highly specialized AI assistant exclusively dedicated to mathematics. "
        "Your ONLY area of expertise is mathematics, including: arithmetic, algebra, calculus, geometry, "
        "trigonometry, linear algebra, statistics, probability, number theory, discrete math, differential "
        "equations, and symbolic computation.\n\n"
        "STRICT RULES YOU MUST FOLLOW:\n"
        "1. If the user asks anything outside of mathematics (e.g. geography, history, biology, coding, "
        "general knowledge, current events, personal advice, etc.), you MUST politely decline and say: "
        "'I am MathGPT, a math-only assistant. I can only help with mathematics topics. "
        "Please ask me a math question!'\n"
        "2. NEVER answer non-math questions, even if you know the answer. Note: Word problems, logic puzzles, and statement-based questions (e.g. 'If 6 workers...') ARE mathematics. Do NOT decline them.\n"
        "3. Use the provided RAG context for math references when relevant.\n"
        "4. When performing symbolic computation, embed a valid SymPy Python code block like `$$sympy:<python code>$$`. Do NOT put natural language inside the sympy block.\n"
        "5. Always return mathematical expressions inside $$...$$ LaTeX blocks.\n"
        "6. Be precise, step-by-step, and educational in your math answers."
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": context},
        {"role": "user", "content": user_msg},
    ]

    # Collect streamed tokens into a full answer string
    answer_parts = []
    async for token in stream_chat(messages):
        answer_parts.append(token)
    answer = "".join(answer_parts)

    sympy_result = None
    if request.use_sympy:
        import re
        match = re.search(r'\$\$sympy:?(.*?)\$\$', answer, re.DOTALL)
        if match:
            sympy_code = match.group(1).strip()
            try:
                latex_result = await process_sympy_blocks(sympy_code)
                if "Error" in latex_result:
                    sympy_result = {
                        "success": False,
                        "error": latex_result
                    }
                else:
                    sympy_result = {
                        "success": True,
                        "result_latex": latex_result
                    }
            except Exception as e:
                sympy_result = {
                    "success": False,
                    "error": str(e)
                }

    # Prepare response matching ChatResponse schema
    # context_chunks is a list of plain strings (from retriever)
    response = {
        "answer": answer,
        "context_used": context_chunks if isinstance(context_chunks, list) else [],
        "sympy_result": sympy_result,
        "model": settings.model_name,
    }
    return response
