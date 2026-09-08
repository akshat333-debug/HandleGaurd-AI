from __future__ import annotations

from typing import Any

from handleguard.privacy.redact import redact_identity
from handleguard.types import Incident


def incident_report_json(incident: Incident) -> dict[str, Any]:
    return {
        "incident_id": incident.incident_id,
        "video_id": incident.video_id,
        "behaviour": incident.behaviour,
        "risk_score": incident.risk_score,
        "risk_level": incident.risk_level.value,
        "confidence": incident.confidence,
        "start_time": incident.start_time,
        "end_time": incident.end_time,
        "zone": incident.zone,
        "loading_bay": incident.loading_bay,
        "primary_object_track": incident.primary_object_track,
        "actor_track": incident.actor_track,
        "evidence": redact_identity(dict(incident.evidence)),
        "explanation": incident.explanation,
        "recommendation": incident.recommendation,
        "status": incident.status.value,
        "clip_path": incident.clip_path,
        "disclaimer": "Decision support only. Not confirmed product damage. No worker identity.",
    }


def incident_report_markdown(incident: Incident) -> str:
    report = incident_report_json(incident)
    evidence_lines = "\n".join(f"- `{k}`: {v}" for k, v in report["evidence"].items()) or "- none"
    return (
        f"# Incident {report['incident_id']}\n\n"
        f"- Behaviour: `{report['behaviour']}`\n"
        f"- Risk: {report['risk_score']:.0f}/100 ({report['risk_level']})\n"
        f"- Confidence: {report['confidence']:.2f}\n"
        f"- Window: {report['start_time']:.1f}s – {report['end_time']:.1f}s\n"
        f"- Bay / zone: {report['loading_bay'] or 'n/a'} / {report['zone'] or 'n/a'}\n"
        f"- Tracks: object `{report['primary_object_track']}`, actor `{report['actor_track']}`\n\n"
        f"## Observed\n\n{report['explanation']}\n\n"
        f"## Evidence\n\n{evidence_lines}\n\n"
        f"## Recommended action\n\n{report['recommendation']}\n\n"
        f"_{report['disclaimer']}_\n"
    )
