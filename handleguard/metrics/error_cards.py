from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorCard:
    incident_id: str
    behaviour: str
    why_system_triggered: str
    why_human_rejected: str
    signal: str
    category: str
    fix: str


def classify_false_positive(reason: str) -> str:
    text = reason.lower()
    if "gentle" in text or "safe handling" in text or "intentional" in text:
        return "intentional_safe_handling"
    if "jitter" in text or "flicker" in text:
        return "tracking_jitter"
    if "occlu" in text:
        return "occlusion"
    if "perspective" in text:
        return "perspective"
    if "threshold" in text:
        return "threshold"
    if "class" in text:
        return "class_confusion"
    if "zone" in text:
        return "zone_geometry"
    if "duplicate" in text:
        return "duplicate_event"
    return "threshold"


def error_card(
    incident_id: str,
    behaviour: str,
    trigger: str,
    rejection: str,
    signal: str,
) -> ErrorCard:
    category = classify_false_positive(rejection)
    return ErrorCard(
        incident_id=incident_id,
        behaviour=behaviour,
        why_system_triggered=trigger,
        why_human_rejected=rejection,
        signal=signal,
        category=category,
        fix="Review YAML thresholds and add a negative example for this pattern.",
    )
