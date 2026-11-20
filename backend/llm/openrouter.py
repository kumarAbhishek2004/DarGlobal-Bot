import os
import json
import logging
import urllib.request
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Primary and automatic fallback OpenRouter free models (prioritizing fast flash models)
FALLBACK_OPENROUTER_MODELS = [
    os.getenv("OPENROUTER_MODEL", "baidu/ernie-5.5-flash-preview:free"),
    "baidu/ernie-5.5-flash-preview:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "liquid/lfm-3-1.7b:free",
    "openrouter/free"
]

class OpenRouterClient:
    """Production client for OpenRouter API with automated multi-model free tier failover."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.getenv("OPENROUTER_API_KEY", "")).strip()

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> Dict[str, Any]:
        """Calls OpenRouter with automatic failover across free models."""
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            logger.error("No valid OPENROUTER_API_KEY found in server environment.")
            return {
                "content": "Configuration Error: `OPENROUTER_API_KEY` is not configured on the server.",
                "model": "none",
                "error": True
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://darglobal.co.uk",
            "X-Title": "DarGlobal Real Estate AI Assistant"
        }

        last_error = ""
        # Deduplicate while preserving order
        seen_models = set()
        active_models = []
        for m in FALLBACK_OPENROUTER_MODELS:
            if m not in seen_models:
                seen_models.add(m)
                active_models.append(m)

        for model in active_models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            try:
                logger.info(f"Dispatching query to OpenRouter model: {model}...")
                req = urllib.request.Request(
                    OPENROUTER_ENDPOINT,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choices = data.get("choices", [])
                    if not choices:
                        continue
                    msg = choices[0].get("message", {})
                    # Extract content, fallback to text or reasoning if reasoning model
                    content = msg.get("content") or msg.get("text") or msg.get("reasoning") or ""
                    
                    if isinstance(content, list):
                        content = "".join([p.get("text", "") for p in content if isinstance(p, dict)])

                    content = str(content).strip() if content is not None else ""
                    
                    if not content:
                        logger.warning(f"Model {model} returned empty content. Trying next fallback...")
                        continue

                    actual_model = data.get("model", model)
                    logger.info(f"Successfully generated answer using: {actual_model}")
                    return {
                        "content": content,
                        "model": actual_model,
                        "usage": data.get("usage", {})
                    }
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {e.code}: {err_text}"
                logger.warning(f"OpenRouter model '{model}' failed ({e.code}). Trying next fallback... Error: {err_text}")
                continue
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Connection error with '{model}': {e}. Trying next fallback...")
                continue

        logger.error(f"All OpenRouter fallback models failed. Last error: {last_error}")
        return {
            "content": f"Unable to reach OpenRouter services. Details: {last_error}",
            "model": "all-fallbacks-exhausted",
            "error": True
        }
