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



    # Retrieve context for the current message
    user_msg = request.message
    context_chunks = retrieve_context(user_msg)
    context = format_context(context_chunks)

    system_prompt = (
        "You are MathGPT — a friendly and highly specialized AI assistant primarily dedicated to mathematics. "
        "Your core expertise is mathematics, including: arithmetic, algebra, calculus, geometry, "
        "trigonometry, linear algebra, statistics, probability, number theory, discrete math, differential "
        "equations, and symbolic computation.\n\n"
        "RULES YOU MUST FOLLOW:\n"
        "1. **Greetings & casual conversation**: If the user says hello, asks how you are, thanks you, "
        "or engages in basic small talk, respond warmly and naturally like a friendly assistant. "
        "You may briefly introduce yourself and your math capabilities. Keep it conversational and varied — "
        "do NOT repeat the same response every time.\n"
        "2. **Non-math knowledge questions**: If the user asks about topics outside mathematics "
        "(e.g. geography, history, biology, physics, chemistry, engineering, finance, economics, coding, programming languages like Python, programming libraries like NumPy, Pandas, Matplotlib, TensorFlow, computer science concepts, AI, machine learning, RAG (Retrieval-Augmented Generation), or how you function, etc.), "
        "you MUST decline in exactly 1 or 2 lines. Do NOT write any code blocks, lists, or detailed explanations.\n"
        "3. **Refusal Format**: When declining, keep the response extremely short (1-2 lines) and state clearly: "
        "'I am sorry, I cannot help you with that because I am only proficient in the explanation of mathematics, not topics other than that.' "
        "Note: Word problems, logic puzzles, and statement-based questions (e.g. 'If 6 workers...') ARE mathematics. Do NOT decline them.\n"
        "4. **No Programming Code**: Absolutely NEVER write general programming code (such as Python scripts, functions, loops, HTML, etc.) to solve or explain math. The ONLY exception is embedding a clean `$$sympy:<python code>$$` block for symbolic math calculations. If a user asks you to write code for a math problem, you MUST decline and use the refusal format.\n"
        "5. Use the provided RAG context for math references when relevant.\n"
        "6. When performing symbolic computation, embed a valid SymPy Python code block like "
        "`$$sympy:<python code>$$`. Do NOT put natural language inside the sympy block.\n"
        "7. Always return mathematical expressions inside $$...$$ LaTeX blocks.\n"
        "8. Be precise, step-by-step, and educational in your math answers.\n"
        "9. Have a warm personality. You can use emojis occasionally. Make users feel welcome."
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt},
    ]
    if context.strip():
        messages.append({"role": "system", "content": f"Here is the retrieved mathematical context to help answer the question if relevant:\n{context}"})
    messages.append({"role": "user", "content": user_msg})

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
