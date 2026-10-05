import os
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any
from ...core.config import get_settings

settings = get_settings()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Roster of active Groq model candidates to try in fallback order
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

async def stream_chat(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Stream tokens from Groq LLM with multi-model fallback and detailed diagnostics."""
    api_key = settings.groq_api_key.strip().strip('"').strip("'")
    if not api_key or api_key == "your_groq_api_key_here":
        yield "⚠️ **Groq API Key is missing or unconfigured.** Please set a valid `GROQ_API_KEY` in your Render Environment Variables."
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build model attempt list (configured model first, followed by fallbacks)
    models_to_try = []
    if settings.model_name:
        models_to_try.append(settings.model_name)
    for m in CANDIDATE_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = ""
    async with httpx.AsyncClient(timeout=60.0) as client:
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 1024,
            }
            try:
                async with client.stream("POST", API_URL, headers=headers, json=payload) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield content
                                except json.JSONDecodeError:
                                    continue
                        return  # Successful streaming complete

                    error_body = await response.aread()
                    err_text = error_body.decode("utf-8", errors="ignore")
                    last_error = f"Status {response.status_code}: {err_text}"
                    print(f"[GROQ WARN] Model '{model}' failed ({response.status_code}): {err_text}")

                    # If 401 Unauthorized, the API key itself is invalid — stop retrying other models
                    if response.status_code == 401:
                        yield (
                            f"⚠️ **Groq API Key Error (401 Unauthorized)**\n\n"
                            f"Your `GROQ_API_KEY` set in Render Environment Variables is invalid or expired.\n\n"
                            f"👉 **Fix**: Go to [console.groq.com](https://console.groq.com) → API Keys → Create a key (starts with `gsk_`) and update `GROQ_API_KEY` in Render."
                        )
                        return

            except Exception as e:
                last_error = str(e)
                print(f"[GROQ EXCEPTION] Model '{model}': {e}")

    # If all candidate models failed
    yield (
        f"⚠️ **Groq API Error**: Could not complete request with available models.\n\n"
        f"**Error Details**: {last_error}\n\n"
        f"👉 Please check your `GROQ_API_KEY` in Render. Make sure your key is active at [console.groq.com](https://console.groq.com) and starts with `gsk_`."
    )


