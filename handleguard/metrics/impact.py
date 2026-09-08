from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AvoidedLoss:
    value: float
    assumption_label: str


def estimated_avoided_loss(n_preventable: float, p_damage: float, cost: float) -> AvoidedLoss:
    return AvoidedLoss(
        value=round(n_preventable * p_damage * cost, 2),
        assumption_label="Assumption, not guaranteed savings. Labelled opportunity only.",
    )
