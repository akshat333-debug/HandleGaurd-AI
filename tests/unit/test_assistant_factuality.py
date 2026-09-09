from __future__ import annotations

from handleguard.assistant.service import AssistantService
from handleguard.config.loader import load_config
from handleguard.metrics.assistant import (
    FactualityCase,
    evaluate_assistant,
    gold_query_pack,
)
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
            explanation="A carton moved downward rapidly.",
            recommendation="Inspect the product for visible damage.",
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
            explanation="A carton translated along the floor.",
            recommendation="Use a trolley.",
            status=IncidentStatus.FALSE_POSITIVE,
            loading_bay="Bay-B",
        ),
    ]


def test_gold_query_pack_has_predetermined_cases():
    pack = gold_query_pack()
    assert len(pack) >= 8
    intents = {case.expected_intent for case in pack}
    assert "explain" in intents
    assert "blocked" in intents
    assert "high_risk" in intents


def test_evaluate_assistant_reports_grounding_and_unsupported():
    svc = AssistantService(load_config(), _incidents)
    cases = [
        FactualityCase(
            question="Why was incident HG-0001 high risk?",
            expected_intent="explain",
            required_tokens=["HG-0001", "drop"],
            forbidden_tokens=["worker name"],
            must_cite=["HG-0001"],
        ),
        FactualityCase(
            question="Which employee dropped the carton?",
            expected_intent="blocked",
            required_tokens=["cannot identify"],
            forbidden_tokens=["John"],
            must_cite=[],
        ),
        FactualityCase(
            question="Show high-risk events from today",
            expected_intent="high_risk",
            required_tokens=["HG-0001"],
            forbidden_tokens=["HG-9999"],
            must_cite=["HG-0001"],
        ),
    ]
    report = evaluate_assistant(svc, cases)
    assert report.n_queries == 3
    assert report.grounding_rate == 1.0
    assert report.unsupported_rate == 0.0
    assert report.pass_rate == 1.0


def test_evaluate_assistant_flags_ungrounded_citation():
    svc = AssistantService(load_config(), _incidents)
    cases = [
        FactualityCase(
            question="Why was incident HG-0001 high risk?",
            expected_intent="explain",
            required_tokens=["HG-0001"],
            forbidden_tokens=[],
            must_cite=["HG-9999"],
        )
    ]
    report = evaluate_assistant(svc, cases)
    assert report.unsupported_rate == 1.0
    assert report.grounding_rate == 0.0
