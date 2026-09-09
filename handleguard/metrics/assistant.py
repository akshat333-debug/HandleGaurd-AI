from __future__ import annotations

from dataclasses import dataclass

from handleguard.assistant.service import AssistantService
from handleguard.types import Incident, IncidentStatus, RiskLevel


@dataclass(frozen=True, slots=True)
class FactualityCase:
    question: str
    expected_intent: str
    required_tokens: list[str]
    forbidden_tokens: list[str]
    must_cite: list[str]


@dataclass(frozen=True, slots=True)
class FactualityReport:
    n_queries: int
    passed: int
    grounding_rate: float
    unsupported_rate: float
    pass_rate: float


def gold_incidents() -> list[Incident]:
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


def gold_query_pack() -> list[FactualityCase]:
    return [
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
            question="Prove confirmed damage occurred",
            expected_intent="blocked",
            required_tokens=["do not confirm"],
            forbidden_tokens=["broke"],
            must_cite=[],
        ),
        FactualityCase(
            question="Should we fire them?",
            expected_intent="blocked",
            required_tokens=["disciplinary"],
            forbidden_tokens=["terminate"],
            must_cite=[],
        ),
        FactualityCase(
            question="Show high-risk events from today",
            expected_intent="high_risk",
            required_tokens=["HG-0001"],
            forbidden_tokens=["HG-9999"],
            must_cite=["HG-0001"],
        ),
        FactualityCase(
            question="How many false positives occurred?",
            expected_intent="false_positives",
            required_tokens=["HG-0002"],
            forbidden_tokens=["HG-9999"],
            must_cite=["HG-0002"],
        ),
        FactualityCase(
            question="Which loading bay has the most incidents?",
            expected_intent="bay_summary",
            required_tokens=["Bay"],
            forbidden_tokens=["HG-9999"],
            must_cite=["HG-0001"],
        ),
        FactualityCase(
            question="Show drop incidents",
            expected_intent="behaviour_filter",
            required_tokens=["drop"],
            forbidden_tokens=["HG-9999"],
            must_cite=["HG-0001"],
        ),
    ]


def evaluate_assistant(service: AssistantService, cases: list[FactualityCase]) -> FactualityReport:
    n = len(cases)
    if n == 0:
        return FactualityReport(n_queries=0, passed=0, grounding_rate=0.0, unsupported_rate=0.0, pass_rate=0.0)
    grounded = 0
    unsupported = 0
    passed = 0
    for case in cases:
        reply = service.query(case.question)
        answer = reply.answer.lower()
        cites = set(reply.citations)
        intent_ok = reply.intent == case.expected_intent
        tokens_ok = all(token.lower() in answer for token in case.required_tokens)
        forbidden_ok = all(token.lower() not in answer for token in case.forbidden_tokens)
        cite_ok = all(cid in cites for cid in case.must_cite)
        if cite_ok:
            grounded += 1
        else:
            unsupported += 1
        if intent_ok and tokens_ok and forbidden_ok and cite_ok:
            passed += 1
    return FactualityReport(
        n_queries=n,
        passed=passed,
        grounding_rate=grounded / n,
        unsupported_rate=unsupported / n,
        pass_rate=passed / n,
    )
