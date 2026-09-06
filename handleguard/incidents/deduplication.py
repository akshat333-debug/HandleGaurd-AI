from __future__ import annotations

from handleguard.config.loader import AppConfig
from handleguard.types import Incident


class Deduplicator:
    def __init__(self, config: AppConfig):
        self.config = config
        self._open: list[Incident] = []

    def accept(self, incident: Incident) -> Incident | None:
        window = self.config.dedup_window(incident.behaviour)
        for existing in self._open:
            if existing.behaviour != incident.behaviour:
                continue
            if existing.primary_object_track != incident.primary_object_track:
                continue
            if abs(incident.start_time - existing.end_time) > window and abs(
                incident.start_time - existing.start_time
            ) > window:
                continue
            if incident.risk_score > existing.risk_score:
                existing.risk_score = incident.risk_score
                existing.risk_level = incident.risk_level
                existing.confidence = max(existing.confidence, incident.confidence)
                existing.explanation = incident.explanation
            existing.end_time = max(existing.end_time, incident.end_time)
            merged = dict(existing.evidence)
            merged.update(incident.evidence)
            existing.evidence = merged
            return None
        self._open.append(incident)
        return incident
