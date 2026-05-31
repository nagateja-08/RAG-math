import os
import json
import httpx
from typing import AsyncGenerator, List, Dict, Any
from ...core.config import get_settings

settings = get_settings()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def stream_chat(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Stream tokens from Groq LLM.

    Parameters
    ----------
    messages: List[Dict[str, str]]
        List of messages in OpenAI chat format, e.g. [{"role": "user", "content": "..."}]

    Yields
    ------
    str
        Individual token strings as they arrive.
    """
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.model_name,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", API_URL, headers=headers, json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        # Groq returns delta content under choices[0].delta.content
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
