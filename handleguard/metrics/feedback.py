from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ReviewLabel:
    incident_id: str
    behaviour: str
    status: str


@dataclass
class BehaviourFeedback:
    confirmed: int = 0
    false_positives: int = 0
    reviewed: int = 0


@dataclass
class FeedbackReport:
    reviewed: int
    confirmed: int
    false_positives: int
    precision: float
    by_behaviour: dict[str, BehaviourFeedback] = field(default_factory=dict)


def feedback_metrics(labels: Iterable[ReviewLabel]) -> FeedbackReport:
    by_behaviour: dict[str, BehaviourFeedback] = {}
    confirmed = 0
    false_positives = 0
    reviewed = 0
    for label in labels:
        status = label.status.upper()
        bucket = by_behaviour.setdefault(label.behaviour, BehaviourFeedback())
        if status in {"CONFIRMED", "FALSE_POSITIVE"}:
            reviewed += 1
            bucket.reviewed += 1
        if status == "CONFIRMED":
            confirmed += 1
            bucket.confirmed += 1
        elif status == "FALSE_POSITIVE":
            false_positives += 1
            bucket.false_positives += 1
    precision = (confirmed / reviewed) if reviewed else 0.0
    return FeedbackReport(
        reviewed=reviewed,
        confirmed=confirmed,
        false_positives=false_positives,
        precision=precision,
        by_behaviour=by_behaviour,
    )
