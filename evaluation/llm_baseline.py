"""Opt-in LLM-as-judge baseline; never used by the production pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass

from services.llm_service import LLMService, LLMServiceException


@dataclass(frozen=True)
class LLMJudgeResult:
    label: str
    raw_response: str


class LLMJudge:
    """Parse a constrained factuality label from an explicitly enabled LLM call."""

    def __init__(self, service: LLMService | None = None, provider: str | None = None) -> None:
        if service is not None:
            self.service = service
        elif provider == "gemini":
            from services.gemini_service import GeminiProvider
            self.service = GeminiProvider()
        else:
            self.service = LLMService()
        self.provider = provider or getattr(self.service, "provider", "groq")
        self.model = getattr(self.service, "model", "unknown")

    def evaluate(self, question: str, response: str) -> LLMJudgeResult:
        prompt = (
            "Classify the response for factual hallucination. Reply with exactly one label: "
            "HALLUCINATION or NO_HALLUCINATION.\n\n"
            f"Question: {question}\nResponse: {response}"
        )
        raw = self.service.generate_response(prompt).strip().upper()
        match = re.search(r"\b(NO_HALLUCINATION|HALLUCINATION)\b", raw)
        if not match:
            raise LLMServiceException("LLM judge returned an invalid classification label.")
        return LLMJudgeResult(match.group(1).lower(), raw)
