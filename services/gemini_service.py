"""Optional Google Gemini provider; never used unless explicitly selected."""
from __future__ import annotations
import os
from utils.env_utils import load_environment

load_environment()

class GeminiServiceException(Exception):
    pass

class GeminiProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-3.6-flash").strip()
        if not self.api_key:
            raise GeminiServiceException("Gemini API key not configured.")
        try:
            from google import genai
            from google.genai import types
            # Match the production Groq client: ignore stale desktop proxy
            # variables unless explicitly enabled for this provider.
            use_proxy = os.environ.get("GEMINI_USE_ENV_PROXY", "false").lower() == "true"
            self._client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(
                    timeout=30_000,
                    client_args={"trust_env": use_proxy},
                ),
            )
        except Exception as exc:
            raise GeminiServiceException("Unable to initialize Gemini provider.") from exc

    def generate_response(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise GeminiServiceException("Please provide a prompt.")
        try:
            response = self._client.models.generate_content(model=self.model, contents=prompt.strip())
            text = getattr(response, "text", None)
            if not text:
                raise GeminiServiceException("Gemini returned an empty response.")
            return text.strip()
        except GeminiServiceException:
            raise
        except Exception as exc:
            detail = str(exc).replace(self.api_key, "[REDACTED]") if self.api_key else str(exc)
            raise GeminiServiceException(f"Gemini request failed: {type(exc).__name__}: {detail[:300]}") from exc
