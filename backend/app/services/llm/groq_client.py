import os
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any
from ...core.config import get_settings

settings = get_settings()

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS_URL = "https://api.groq.com/openai/v1/models"

# Cache active models list in memory
_cached_models: List[str] = []

async def get_available_models(api_key: str) -> List[str]:
    """Fetch live list of active model IDs from Groq API."""
    global _cached_models
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(MODELS_URL, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                model_objs = data.get("data", [])
                active_ids = [m["id"] for m in model_objs if isinstance(m, dict) and "id" in m]
                if active_ids:
                    _cached_models = active_ids
                    return active_ids
            elif resp.status_code == 401:
                return []
    except Exception as e:
        print(f"[GROQ WARN] Failed to fetch live models list: {e}")

    return _cached_models


async def stream_chat(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Stream tokens from Groq LLM with dynamic live model discovery."""
    api_key = settings.groq_api_key.strip().strip('"').strip("'")
    if not api_key or api_key == "your_groq_api_key_here":
        yield "⚠️ **Groq API Key is missing or unconfigured.** Please set a valid `GROQ_API_KEY` in your Render Environment Variables."
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Query live models for this API key
    live_models = await get_available_models(api_key)

    if not live_models:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                test_resp = await client.get(MODELS_URL, headers=headers)
                if test_resp.status_code == 401:
                    yield (
                        f"⚠️ **Groq API Key Error (401 Unauthorized)**\n\n"
                        f"Your `GROQ_API_KEY` set in Render Environment Variables is invalid or expired.\n\n"
                        f"👉 **Fix**: Go to [console.groq.com](https://console.groq.com) → API Keys → Create a key (starts with `gsk_`) and update `GROQ_API_KEY` in Render."
                    )
                    return
            except Exception:
                pass

    # Preferred fallback order
    preferred = [
        settings.model_name,
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.2-11b-vision-instruct",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "qwen-2.5-coder-32b",
        "deepseek-r1-distill-llama-70b",
    ]

    models_to_try: List[str] = []
    for p in preferred:
        if p and (not live_models or p in live_models) and p not in models_to_try:
            models_to_try.append(p)

    for lm in live_models:
        if lm not in models_to_try:
            models_to_try.append(lm)

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
                        return  # Success!

                    error_body = await response.aread()
                    err_text = error_body.decode("utf-8", errors="ignore")
                    last_error = f"Model '{model}' ({response.status_code}): {err_text}"
                    print(f"[GROQ WARN] Model '{model}' failed ({response.status_code}): {err_text}")

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

    yield (
        f"⚠️ **Groq API Error**: Could not complete request with available models.\n\n"
        f"**Details**: {last_error}\n\n"
        f"👉 Please verify your `GROQ_API_KEY` in Render. Get a free key at [console.groq.com](https://console.groq.com)."
    )



