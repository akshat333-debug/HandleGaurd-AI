from __future__ import annotations

from handleguard.incidents.reports import incident_report_json, incident_report_markdown
from handleguard.privacy.redact import redact_identity
from handleguard.types import Incident, IncidentStatus, RiskLevel


def _incident() -> Incident:
    return Incident(
        incident_id="HG-0001",
        video_id="vid-1",
        behaviour="drop",
        risk_score=82.0,
        risk_level=RiskLevel.CRITICAL,
        confidence=0.88,
        start_time=4.2,
        end_time=4.8,
        primary_object_track="carton_8",
        actor_track="person_3",
        equipment_track=None,
        zone="staging",
        evidence={"drop_distance_px": 91, "worker_name": "Alex"},
        explanation="A carton moved downward rapidly.",
        recommendation="Inspect the product for visible damage.",
        status=IncidentStatus.NEW,
        loading_bay="Bay-A",
        clip_path="data/clips/incident_20260904_HG-0001.mp4",
        supervisor_note="Check bay markings",
    )


def test_json_report_contains_required_fields():
    report = incident_report_json(_incident())
    assert report["incident_id"] == "HG-0001"
    assert report["behaviour"] == "drop"
    assert report["risk_score"] == 82.0
    assert report["confidence"] == 0.88
    assert report["risk_level"] == "Critical"
    assert "explanation" in report
    assert "recommendation" in report
    assert "worker_name" not in report["evidence"]


def test_markdown_report_is_evidence_based():
    md = incident_report_markdown(_incident())
    assert "# Incident HG-0001" in md
    assert "drop" in md
    assert "82" in md
    assert "0.88" in md
    assert "Alex" not in md
    assert "decision support" in md.lower() or "not confirmed damage" in md.lower()


def test_redact_identity_strips_names_and_ids():
    payload = {
        "worker_name": "Alex",
        "employee_id": "E-22",
        "face_id": "abc",
        "drop_distance_px": 91,
        "note": "person_3 handled carton_8",
    }
    cleaned = redact_identity(payload)
    assert "worker_name" not in cleaned
    assert "employee_id" not in cleaned
    assert "face_id" not in cleaned
    assert cleaned["drop_distance_px"] == 91
    assert "person_3" in cleaned["note"]
