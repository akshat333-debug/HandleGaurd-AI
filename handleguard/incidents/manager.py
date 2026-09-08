from __future__ import annotations

from itertools import count

from datetime import datetime, timezone

from handleguard.config.loader import AppConfig
from handleguard.incidents.clips import plan_clip
from handleguard.incidents.deduplication import Deduplicator
from handleguard.incidents.explain import explain_incident, recommend_action
from handleguard.risk.scorer import score_risk
from handleguard.types import BehaviourEvidence, Incident, IncidentStatus, is_person


class IncidentEngine:
    def __init__(self, config: AppConfig, video_id: str = "unknown", video_duration: float = 12.0):
        self.config = config
        self.video_id = video_id
        self.video_duration = video_duration
        self.deduplicator = Deduplicator(config)
        self._ids = count(1)
        self.incidents: list[Incident] = []
        self._repeat: dict[str, int] = {}

    def ingest(
        self,
        evidence: BehaviourEvidence,
        *,
        product_class: str = "default",
        zone_type: str | None = None,
        zone_name: str | None = None,
        camera_id: str = "cam-01",
        loading_bay: str | None = None,
    ) -> Incident | None:
        primary = next((e for e in evidence.entities if not e.startswith("person")), evidence.entities[0] if evidence.entities else None)
        actor = next((e for e in evidence.entities if is_person(e.split("_")[0])), None)
        key = f"{evidence.behaviour}:{primary}"
        self._repeat[key] = self._repeat.get(key, 0) + 1
        risk = score_risk(
            evidence,
            self.config,
            product_class=product_class,
            zone_type=zone_type,
            repeat_count=self._repeat[key],
        )
        incident = Incident(
            incident_id=f"HG-{self._ids.__next__():04d}",
            video_id=self.video_id,
            behaviour=evidence.behaviour,
            risk_score=risk.score,
            risk_level=risk.level,
            confidence=risk.confidence,
            start_time=evidence.start_time,
            end_time=evidence.end_time,
            primary_object_track=primary,
            actor_track=actor,
            equipment_track=None,
            zone=zone_name,
            evidence=dict(evidence.evidence),
            explanation=explain_incident(evidence, risk),
            recommendation=recommend_action(evidence.behaviour, self.config),
            status=IncidentStatus.NEW,
            camera_id=camera_id,
            loading_bay=loading_bay,
        )
        clip = plan_clip(
            incident.incident_id,
            incident.start_time,
            incident.end_time,
            self.video_duration,
            created_at=datetime.now(timezone.utc),
        )
        incident.clip_path = f"data/clips/{clip.filename}"
        incident.thumbnail_path = incident.clip_path.replace(".mp4", ".jpg")
        accepted = self.deduplicator.accept(incident)
        if accepted is None:
            return None
        self.incidents.append(accepted)
        return accepted
