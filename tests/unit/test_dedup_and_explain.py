from __future__ import annotations

from handleguard.config.loader import load_config
from handleguard.incidents.deduplication import Deduplicator
from handleguard.incidents.explain import explain_incident, recommend_action
from handleguard.incidents.manager import IncidentEngine
from handleguard.risk.scorer import score_risk
from handleguard.types import BehaviourEvidence, Incident, IncidentStatus, RiskLevel


def _incident(start: float, end: float, risk: float = 70) -> Incident:
    return Incident(
        incident_id="HG-0001",
        video_id="v1",
        behaviour="drop",
        risk_score=risk,
        risk_level=RiskLevel.HIGH,
        confidence=0.8,
        start_time=start,
        end_time=end,
        primary_object_track="carton_1",
        actor_track=None,
        equipment_track=None,
        zone=None,
        evidence={"drop_distance_px": 90},
        explanation="x",
        recommendation="y",
        status=IncidentStatus.NEW,
    )


def test_dedup_merges_same_track_inside_window():
    cfg = load_config()
    dedup = Deduplicator(cfg)
    first = dedup.accept(_incident(1.0, 1.2, 60))
    second = dedup.accept(_incident(1.5, 1.8, 80))
    assert first is not None
    assert second is None
    assert first.risk_score == 80
    assert first.end_time == 1.8


def test_dedup_keeps_separate_tracks():
    cfg = load_config()
    dedup = Deduplicator(cfg)
    a = _incident(1.0, 1.2)
    b = _incident(1.1, 1.3)
    b.incident_id = "HG-0002"
    b.primary_object_track = "carton_2"
    assert dedup.accept(a) is not None
    assert dedup.accept(b) is not None


def test_explanation_is_evidence_based_not_intent():
    cfg = load_config()
    evidence = BehaviourEvidence(
        behaviour="drop",
        start_time=4.2,
        end_time=4.8,
        entities=["carton_8"],
        raw_score=0.86,
        evidence={"drop_distance_px": 91, "peak_speed": 141, "duration_s": 0.6},
    )
    risk = score_risk(evidence, cfg)
    text = explain_incident(evidence, risk)
    assert "drop" in text.lower()
    assert "91" in text
    assert "careless" not in text.lower()
    assert "employee" not in text.lower()


def test_recommend_action_uses_sop():
    cfg = load_config()
    rec = recommend_action("drag", cfg)
    assert "trolley" in rec.lower() or "pallet" in rec.lower()


def test_incident_engine_assigns_ids():
    engine = IncidentEngine(load_config(), video_id="v1")
    evidence = BehaviourEvidence("zone_violation", 1.0, 3.0, ["carton_1"], 0.7, {"zone": "walkway", "duration_s": 2})
    first = engine.ingest(evidence, product_class="carton")
    assert first is not None
    assert first.incident_id.startswith("HG-")
