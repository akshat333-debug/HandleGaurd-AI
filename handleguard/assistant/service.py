from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from handleguard.assistant.guardrails import blocked_reason
from handleguard.config.loader import AppConfig
from handleguard.types import Incident


@dataclass(slots=True)
class AssistantReply:
    answer: str
    citations: list[str]
    blocked: bool = False
    intent: str = "general"


def _matches(incident: Incident, term: str) -> bool:
    blob = " ".join(
        [
            incident.behaviour,
            incident.incident_id,
            incident.risk_level.value,
            incident.zone or "",
            incident.loading_bay or "",
            incident.explanation,
        ]
    ).lower()
    return term.lower() in blob


class AssistantService:
    def __init__(
        self,
        config: AppConfig,
        incident_loader: Callable[[], Iterable[Incident]],
    ):
        self.config = config
        self.incident_loader = incident_loader

    def query(self, question: str) -> AssistantReply:
        blocked = blocked_reason(question)
        if blocked:
            return AssistantReply(answer=blocked, citations=[], blocked=True, intent="blocked")

        incidents = list(self.incident_loader())
        q = question.lower().strip()
        if not incidents:
            return AssistantReply(
                answer="No matching incidents were found.",
                citations=[],
                intent="empty",
            )

        if q.startswith("why") or any(i.incident_id.lower() in q for i in incidents):
            picked = [i for i in incidents if i.incident_id.lower() in q]
            if not picked:
                picked = incidents[:1]
            intent = "explain"
        elif "high-risk" in q or "high risk" in q or "critical" in q:
            picked = [i for i in incidents if i.risk_level.value in {"High", "Critical"}]
            intent = "high_risk"
        elif "false positive" in q:
            picked = [i for i in incidents if i.status.value == "FALSE_POSITIVE"]
            intent = "false_positives"
        elif "bay" in q:
            picked = incidents
            intent = "bay_summary"
        elif any(i.behaviour in q for i in incidents) or any(
            name in q
            for name in (
                "drop",
                "drag",
                "throw",
                "stack",
                "zone",
                "overhang",
                "stepping",
                "sequence",
                "surface",
            )
        ):
            picked = [i for i in incidents if _matches(i, q.split()[-1]) or i.behaviour.replace("_", " ") in q]
            if not picked:
                picked = [i for i in incidents if any(_matches(i, token) for token in q.split() if len(token) > 3)]
            intent = "behaviour_filter"
        else:
            picked = incidents[:8]
            intent = "summary"

        if not picked:
            return AssistantReply(
                answer="No matching incidents were found.",
                citations=[],
                intent=intent,
            )

        citations = [i.incident_id for i in picked[:8]]
        if intent == "bay_summary":
            counts: dict[str, int] = {}
            for item in incidents:
                key = item.loading_bay or "unknown"
                counts[key] = counts.get(key, 0) + 1
            ranking = ", ".join(f"{k} ({v})" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
            answer = f"Incident counts by loading bay: {ranking}. Citations: {', '.join(citations)}."
        elif intent == "explain":
            item = picked[0]
            answer = (
                f"{item.incident_id} is {item.behaviour} at t={item.start_time:.1f}s "
                f"with risk {item.risk_score:.0f}/100 ({item.risk_level.value}) "
                f"and confidence {item.confidence:.2f}. {item.explanation}"
            )
        else:
            lines = [
                f"{i.incident_id}: {i.behaviour} risk {i.risk_score:.0f} ({i.risk_level.value})"
                for i in picked[:6]
            ]
            answer = (
                f"Found {len(picked)} matching incident(s). "
                + " ".join(lines)
                + " These are observed risk events, not confirmed damage or worker identity."
            )
        return AssistantReply(answer=answer, citations=citations, intent=intent)
