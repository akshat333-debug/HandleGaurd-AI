from __future__ import annotations

from collections import defaultdict

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.zones import resolve_zone
from handleguard.types import BehaviourEvidence, ZoneType, is_product


class UnsafeSurfaceDetector:
    name = "unsafe_surface"

    def __init__(self) -> None:
        self._entered: dict[str, float] = {}

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
            moving = abs(track.velocity[0]) + abs(track.velocity[1]) > 8
            zone = resolve_zone(track.bbox, context.zones)
            if zone is None or zone.zone_type != ZoneType.UNSAFE_SURFACE or not moving:
                continue
            key = f"{track.track_id}:{zone.name}"
            active.add(key)
            self._entered.setdefault(key, context.timestamp)
            dwell = context.timestamp - self._entered[key]
            if dwell >= min_dur:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=self._entered[key],
                        end_time=context.timestamp,
                        entities=[track.track_id],
                        raw_score=min(1.0, dwell / (min_dur * 2)),
                        evidence={"zone": zone.name, "duration_s": round(dwell, 3)},
                    )
                )
        for key in [k for k in self._entered if k not in active]:
            del self._entered[key]
        return out
