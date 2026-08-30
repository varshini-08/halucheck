"""Statistical summaries for measured evaluation timings."""

from __future__ import annotations

from statistics import median
from typing import Iterable


def summarize_timings(values: Iterable[float]) -> dict[str, float | int]:
    timings = [float(value) for value in values]
    if not timings:
        return {"count": 0, "average_seconds": 0.0, "minimum_seconds": 0.0, "maximum_seconds": 0.0, "median_seconds": 0.0, "samples_per_second": 0.0}
    average = sum(timings) / len(timings)
    return {
        "count": len(timings),
        "average_seconds": average,
        "minimum_seconds": min(timings),
        "maximum_seconds": max(timings),
        "median_seconds": median(timings),
        "samples_per_second": 1.0 / average if average else 0.0,
    }
