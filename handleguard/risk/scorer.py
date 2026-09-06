from __future__ import annotations

from dataclasses import dataclass

from handleguard.config.loader import AppConfig
from handleguard.types import BehaviourEvidence, RiskLevel, ZoneType


@dataclass(slots=True, frozen=True)
class RiskResult:
    score: float
    level: RiskLevel
    confidence: float
    components: dict[str, float]


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def risk_level_for(score: float) -> RiskLevel:
    if score <= 24:
        return RiskLevel.LOW
    if score <= 49:
        return RiskLevel.MEDIUM
    if score <= 74:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _location_risk(zone_type: str | None, config: AppConfig) -> float:
    table = config.risk_weights.get("location_risk", {})
    key = zone_type or "unknown"
    return float(table.get(key, table.get("unknown", 0.30)))


def score_risk(
    evidence: BehaviourEvidence,
    config: AppConfig,
    *,
    product_class: str = "default",
    zone_type: str | None = None,
    repeat_count: int = 1,
) -> RiskResult:
    weights = config.risk_weights.get("weights", {})
    behaviour_cfg = config.behaviour(evidence.behaviour)
    severity = float(behaviour_cfg.get("behaviour_severity", 0.5))
    intensity = _clip(float(evidence.raw_score))
    fragility = float(config.product_meta(product_class).get("fragility", 0.4))
    duration_s = float(evidence.evidence.get("duration_s", evidence.end_time - evidence.start_time))
    duration = _clip(duration_s / 4.0)
    frequency = _clip((repeat_count - 1) * 0.25)
    location = _clip(_location_risk(zone_type, config))

    raw = (
        float(weights.get("behaviour_severity", 0.35)) * severity
        + float(weights.get("intensity", 0.20)) * intensity
        + float(weights.get("product_fragility", 0.15)) * fragility
        + float(weights.get("duration", 0.10)) * duration
        + float(weights.get("repeat_frequency", 0.10)) * frequency
        + float(weights.get("location_risk", 0.10)) * location
    )
    score = round(_clip(raw) * 100.0, 2)
    confidence = round(_clip(0.35 + 0.65 * intensity), 3)
    return RiskResult(
        score=score,
        level=risk_level_for(score),
        confidence=confidence,
        components={
            "behaviour_severity": severity,
            "intensity": intensity,
            "product_fragility": fragility,
            "duration": duration,
            "repeat_frequency": frequency,
            "location_risk": location,
        },
    )
