from __future__ import annotations

from collections import defaultdict

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.zones import resolve_zone
from handleguard.types import BehaviourEvidence, ZoneType, is_product


class ZoneViolationDetector:
    name = "zone_violation"

    def __init__(self) -> None:
        self._entered: dict[str, float] = defaultdict(float)

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_dur = float(cfg["min_duration_seconds"])
        out: list[BehaviourEvidence] = []
        active: set[str] = set()
        for track in context.tracks:
            if not is_product(track.class_name):
                continue
            zone = resolve_zone(track.bbox, context.zones)
            track.zone = zone.name if zone else None
            if zone is None:
                continue
            if zone.zone_type not in {ZoneType.RESTRICTED, ZoneType.RESTRICTED_PRODUCT}:
                continue
            key = f"{track.track_id}:{zone.name}"
            active.add(key)
            if key not in self._entered:
                self._entered[key] = context.timestamp
            dwell = context.timestamp - self._entered[key]
            if dwell >= min_dur:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=self._entered[key],
                        end_time=context.timestamp,
                        entities=[track.track_id],
                        raw_score=min(1.0, dwell / (min_dur * 2)),
                        evidence={
                            "zone": zone.name,
                            "zone_type": zone.zone_type.value,
                            "duration_s": round(dwell, 3),
                        },
                    )
                )
        stale = [key for key in self._entered if key not in active]
        for key in stale:
            del self._entered[key]
        return out
