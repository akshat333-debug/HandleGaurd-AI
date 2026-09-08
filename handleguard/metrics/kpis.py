from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ShiftKpis:
    high_risk_events: int
    false_positive_rate: float
    high_risk_per_100: float
    mean_response_s: float
    primary_kpi: str


def high_risk_per_100(high_risk_events: int, handling_actions: int) -> float:
    if handling_actions <= 0:
        return 0.0
    return round(100.0 * high_risk_events / handling_actions, 4)


def shift_kpis(
    *,
    total_incidents: int,
    high_risk: int,
    critical: int,
    false_positives: int,
    confirmed: int,
    handling_actions: int,
    mean_response_s: float,
) -> ShiftKpis:
    high_risk_events = high_risk + critical
    reviewed = confirmed + false_positives
    fp_rate = (false_positives / reviewed) if reviewed else 0.0
    return ShiftKpis(
        high_risk_events=high_risk_events,
        false_positive_rate=fp_rate,
        high_risk_per_100=high_risk_per_100(high_risk_events, handling_actions),
        mean_response_s=mean_response_s,
        primary_kpi="High-risk handling events identified early enough for intervention",
    )
