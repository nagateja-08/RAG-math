import os
import logging
from typing import List, Dict, Generator, Optional
from groq import Groq
from ...core.config import get_settings

logger = logging.getLogger("mathgpt.llm")
settings = get_settings()

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it"
]

def get_groq_client() -> Optional[Groq]:
    api_key = settings.groq_api_key
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)

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
