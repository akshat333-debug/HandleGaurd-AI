from __future__ import annotations

from handleguard.assistant.service import AssistantService
from handleguard.config.loader import load_config
from handleguard.types import Incident, IncidentStatus, RiskLevel


def _incidents():
    return [
        Incident(
            incident_id="HG-0001",
            video_id="v1",
            behaviour="drop",
            risk_score=82,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.88,
            start_time=4.2,
            end_time=4.8,
            primary_object_track="carton_1",
            actor_track=None,
            equipment_track=None,
            zone="staging",
            evidence={},
            explanation="potential drop",
            recommendation="inspect",
            status=IncidentStatus.NEW,
            loading_bay="Bay-A",
        ),
        Incident(
            incident_id="HG-0002",
            video_id="v1",
            behaviour="drag",
            risk_score=40,
            risk_level=RiskLevel.MEDIUM,
            confidence=0.7,
            start_time=6.0,
            end_time=7.0,
            primary_object_track="carton_2",
            actor_track=None,
            equipment_track=None,
            zone="walkway",
            evidence={},
            explanation="potential drag",
            recommendation="use trolley",
            status=IncidentStatus.FALSE_POSITIVE,
            loading_bay="Bay-B",
        ),
    ]


def test_blocks_identity_request():
    svc = AssistantService(load_config(), _incidents)
    reply = svc.query("Which employee dropped the carton?")
    assert reply.blocked is True
    assert "cannot identify" in reply.answer.lower() or "not people" in reply.answer.lower()


def test_blocks_confirmed_damage_claim():
    svc = AssistantService(load_config(), _incidents)
    reply = svc.query("Prove confirmed damage occurred")
    assert reply.blocked is True


def test_empty_store():
    svc = AssistantService(load_config(), lambda: [])
    reply = svc.query("Show drop incidents")
    assert reply.answer == "No matching incidents were found."


def test_high_risk_query_cites_ids():
    svc = AssistantService(load_config(), _incidents)
    reply = svc.query("Show high-risk events from today")
    assert "HG-0001" in reply.citations
    assert reply.blocked is False


def test_false_positive_query():
    svc = AssistantService(load_config(), _incidents)
    reply = svc.query("How many false positives occurred?")
    assert "HG-0002" in reply.citations
