"""Independent, opt-in baseline adapters for research evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from verification.nli_verifier import NLIResult, NLIVerifier


class BaselineUnavailable(RuntimeError):
    """Raised when a baseline lacks the inputs required by its protocol."""


@dataclass(frozen=True)
class SelfCheckResult:
    score: float
    label: str
    comparisons: int


class SelfCheckNLIBaseline:
    """SelfCheck-style NLI scorer over independently supplied response samples."""

    def __init__(self, verifier: NLIVerifier | None = None) -> None:
        self.verifier = verifier or NLIVerifier()

    def score(self, fact: str, sampled_responses: Sequence[str]) -> SelfCheckResult:
        responses = [response.strip() for response in sampled_responses if response and response.strip()]
        if len(responses) < 2:
            raise BaselineUnavailable("SelfCheckNLI requires at least two independently sampled responses.")
        results: list[NLIResult] = [self.verifier.verify(responses[0], fact)]
        results.extend(self.verifier.verify(response, fact) for response in responses[1:])
        contradiction = sum(result.probabilities.get("CONTRADICTED", 0.0) for result in results) / len(results)
        label = "hallucination" if contradiction >= 0.5 else "no_hallucination"
        return SelfCheckResult(contradiction, label, len(results))
