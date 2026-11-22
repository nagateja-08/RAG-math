import os
import logging
from typing import List, Dict, Generator, Optional
from groq import Groq
from ...core.config import get_settings

logger = logging.getLogger("mathgpt.llm")
settings = get_settings()

FALLBACK_MODELS = [
    "qwen/qwen3.8-27b",             # Primary — Best active math model on Groq
    "openai/gpt-oss-120b",          # 120B model fallback
    "openai/gpt-oss-20b",           # 20B fast fallback
    "llama-3.3-70b-versatile",      # Meta LLaMA 3.3
    "llama-3.1-8b-instant",         # LLaMA 3.1 instant
]

def get_groq_client() -> Optional[Groq]:
    api_key = settings.groq_api_key
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)

def extract_math_from_image(image_data: str) -> Optional[str]:
    """
    Extract and transcribe mathematical equations, problems, or questions from an image.
    Supports base64 data URLs ('data:image/...;base64,...') or raw base64.
    Uses multimodal Qwen vision on Groq.
    """
    client = get_groq_client()
    if not client:
        logger.warning("Groq client not available for image vision extraction.")
        return None

    # Format data URL if needed
    if not image_data.startswith("data:image/"):
        image_url = f"data:image/jpeg;base64,{image_data}"
    else:
        image_url = image_data

    prompt = (
        "You are an expert mathematical OCR and problem extractor. "
        "Carefully inspect the image and transcribe the mathematical problem, question, or equations exactly. "
        "Extract all variables, numbers, operations, symbols, and written instructions precisely. "
        "Format mathematical expressions using standard LaTeX notation ($...$ or $$...$$). "
        "Return ONLY the transcribed mathematical question or problem, with no introductory text or conversational filler."
    )

    # Models with vision capability on Groq
    vision_models = ["qwen/qwen3.8-27b"]

    for model in vision_models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=600
            )
            extracted = response.choices[0].message.content.strip()
            if extracted:
                logger.info(f"Successfully transcribed math problem from image using {model}: {extracted[:120]}")
                return extracted
        except Exception as e:
            logger.warning(f"Image vision transcription failed with {model}: {e}")
            continue

    return None

def chat_completion(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 2048) -> str:
    """Execute Groq chat completion with model fallback cascade."""
    client = get_groq_client()
    if not client:
        return (
            "Groq API Key is not configured. Please set a valid `GROQ_API_KEY` in `backend/.env` "
            "to enable real-time mathematical reasoning and LLM synthesis."
        )

    models_to_try = [settings.model_name] + [m for m in FALLBACK_MODELS if m != settings.model_name]
    last_error = None

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq generation failed with model '{model}': {e}. Attempting fallback...")
            last_error = e

    return f"LLM Generation Error across all attempted models: {last_error}"

def stream_chat(messages: List[Dict[str, str]], temperature: float = 0.2) -> Generator[str, None, None]:
    """Stream response tokens from Groq."""
    client = get_groq_client()
    if not client:
        yield "Groq API Key is not configured in backend/.env"
        return

    models_to_try = [settings.model_name] + [m for m in FALLBACK_MODELS if m != settings.model_name]
    for model in models_to_try:
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
                stream=True
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield token
            return
        except Exception as e:
            logger.warning(f"Groq streaming failed with {model}: {e}")
            continue

    yield "Error generating response from LLM."
