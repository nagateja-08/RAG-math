import os
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any
from ...core.config import get_settings

settings = get_settings()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def stream_chat(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Stream tokens from Groq LLM with robust error reporting."""
    api_key = settings.groq_api_key.strip().strip('"').strip("'")
    if not api_key or api_key == "your_groq_api_key_here":
        yield "⚠️ **Groq API Key is missing or unconfigured.** Please set a valid `GROQ_API_KEY` in your Render Environment Variables."
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.model_name,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", API_URL, headers=headers, json=payload) as response:
                if response.status_code == 404:
                    # Model not found / unavailable on this API key — fall back to universally supported model
                    print(f"[GROQ WARN] Model '{payload['model']}' 404. Falling back to 'llama-3.1-8b-instant'...")
                    payload["model"] = "llama-3.1-8b-instant"
                    async with client.stream("POST", API_URL, headers=headers, json=payload) as fallback_resp:
                        if fallback_resp.status_code != 200:
                            err_text = (await fallback_resp.aread()).decode("utf-8", errors="ignore")
                            yield f"⚠️ **Groq API Error ({fallback_resp.status_code})**: {err_text}"
                            return
                        async for line in fallback_resp.aiter_lines():
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
                        return

                if response.status_code != 200:
                    error_body = await response.aread()
                    err_text = error_body.decode("utf-8", errors="ignore")
                    print(f"[GROQ ERROR] Status {response.status_code}: {err_text}")
                    yield f"⚠️ **Groq API Error ({response.status_code})**: {err_text}"
                    return

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
    except Exception as e:
        print(f"[GROQ EXCEPTION] {e}")
        yield f"⚠️ **Connection Error**: Failed to reach Groq API: {str(e)}"

