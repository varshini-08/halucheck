"""Groq response generation service."""

import os
from typing import Any, Iterable, Optional

import groq
import httpx
from utils.env_utils import load_environment

load_environment()


class LLMServiceException(Exception):
    """Raised when Groq generation cannot complete."""


class GroqProvider:
    """Minimal Groq Python SDK client for the project model."""

    def __init__(self, api_key: str, model: str = "openai/gpt-oss-20b") -> None:
        self.api_key = api_key
        self.model = model
        # Some desktop environments inject proxy variables that point at a
        # stopped local proxy. Bypass them by default, while retaining an
        # explicit opt-in for managed networks that require a proxy.
        use_environment_proxy = os.environ.get("GROQ_USE_ENV_PROXY", "false").lower() == "true"
        self._client = groq.Client(
            api_key=self.api_key,
            http_client=httpx.Client(trust_env=use_environment_proxy),
        )

    def generate_response(self, question: str) -> str:
        if not self.api_key:
            raise LLMServiceException("Groq API key not configured.")

        prompt = question.strip()
        if not prompt:
            raise LLMServiceException("Please provide a question.")

        try:
            completion = self._client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
                max_completion_tokens=512,
                timeout=30,
            )
            return self._extract_text(completion)
        except groq.GroqError as exc:
            raise LLMServiceException(str(exc)) from exc
        except Exception as exc:
            raise LLMServiceException(str(exc)) from exc

    @staticmethod
    def _extract_text(completion: Any) -> str:
        if not getattr(completion, "choices", None):
            raise LLMServiceException("Groq returned an unexpected response.")

        first_choice = completion.choices[0]
        message = getattr(first_choice, "message", None)
        if not message or not getattr(message, "content", None):
            raise LLMServiceException("Groq returned an unexpected response.")

        text = message.content.strip()
        if not text:
            raise LLMServiceException("Groq returned an empty response.")
        return text


class LLMService:
    """Application-facing Groq service; no provider or model selection."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.provider = os.environ.get("LLM_PROVIDER", "groq").strip().lower()
        if self.provider == "gemini":
            from services.gemini_service import GeminiProvider
            self.model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash").strip()
            self._client = GeminiProvider(api_key or os.environ.get("GEMINI_API_KEY", ""), self.model)
            return
        if self.provider != "groq":
            raise LLMServiceException("LLM_PROVIDER must be 'groq' or 'gemini'.")
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b").strip()
        self._client = GroqProvider(self.api_key, self.model)

    def generate_response(self, question: str) -> str:
        if self.provider == "gemini":
            return self._client.generate_response(question)
        return self._client.generate_response(question)
