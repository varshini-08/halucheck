"""Conservative evaluation cost metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostSummary:
    """Counts that can be measured without assuming provider pricing."""

    llm_requests: int
    wikipedia_requests: int
    nli_inferences: int
    estimated_cost: str = "Cost unavailable"


def summarize(rows: list[dict]) -> CostSummary:
    """Summarize explicitly recorded calls without fabricating prices."""
    return CostSummary(
        llm_requests=0,
        wikipedia_requests=sum(int(row.get("wikipedia_request_count", 0)) for row in rows),
        nli_inferences=sum(int(row.get("nli_inference_count", 0)) for row in rows),
    )
