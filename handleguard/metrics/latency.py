from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LatencyStats:
    mean: float
    p50: float
    p95: float
    count: int


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if pct <= 0:
        return sorted_values[0]
    k = max(1, math.ceil((pct / 100.0) * len(sorted_values)))
    return sorted_values[min(k - 1, len(sorted_values) - 1)]


def summarize_latencies(values_ms: list[float]) -> LatencyStats:
    if not values_ms:
        return LatencyStats(mean=0.0, p50=0.0, p95=0.0, count=0)
    ordered = sorted(values_ms)
    mean = sum(ordered) / len(ordered)
    return LatencyStats(
        mean=round(mean, 6),
        p50=round(_percentile(ordered, 50), 6),
        p95=round(_percentile(ordered, 95), 6),
        count=len(ordered),
    )
