from __future__ import annotations

from handleguard.config.loader import load_config
from handleguard.risk.scorer import risk_level_for, score_risk
from handleguard.types import BehaviourEvidence, RiskLevel


def _evidence(behaviour: str = "drop", raw: float = 0.9) -> BehaviourEvidence:
    return BehaviourEvidence(
        behaviour=behaviour,
        start_time=1.0,
        end_time=1.6,
        entities=["carton_1"],
        raw_score=raw,
        evidence={"duration_s": 0.6, "drop_distance_px": 90},
    )


def test_risk_level_bands():
    assert risk_level_for(0) is RiskLevel.LOW
    assert risk_level_for(24) is RiskLevel.LOW
    assert risk_level_for(25) is RiskLevel.MEDIUM
    assert risk_level_for(50) is RiskLevel.HIGH
    assert risk_level_for(75) is RiskLevel.CRITICAL
    assert risk_level_for(100) is RiskLevel.CRITICAL


def test_score_risk_separates_confidence():
    cfg = load_config()
    result = score_risk(_evidence(), cfg, product_class="glass", zone_type="restricted")
    assert 0 <= result.score <= 100
    assert 0 <= result.confidence <= 1
    assert result.confidence != result.score
    assert result.components["product_fragility"] == 1.0


def test_higher_intensity_increases_risk():
    cfg = load_config()
    low = score_risk(_evidence(raw=0.1), cfg)
    high = score_risk(_evidence(raw=1.0), cfg)
    assert high.score > low.score
