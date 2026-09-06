from __future__ import annotations

from collections import defaultdict

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import bbox_bottom_center, point_in_polygon
from handleguard.types import BehaviourEvidence, is_person, is_product


class SteppingDetector:
    name = "stepping"

    def __init__(self) -> None:
        self._started: dict[str, float] = defaultdict(float)

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_dur = float(cfg["min_duration_seconds"])
        people = [t for t in context.tracks if is_person(t.class_name)]
        products = [t for t in context.tracks if is_product(t.class_name)]
        out: list[BehaviourEvidence] = []
        active: set[str] = set()
        for person in people:
            foot = bbox_bottom_center(person.bbox)
            for product in products:
                x1, y1, x2, y2 = product.bbox
                polygon = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                top_band = [(x1, y1), (x2, y1), (x2, y1 + (y2 - y1) * 0.45), (x1, y1 + (y2 - y1) * 0.45)]
                if not (point_in_polygon(foot, polygon) or point_in_polygon(foot, top_band)):
                    in_x = x1 <= foot[0] <= x2
                    in_y = y1 <= foot[1] <= y2
                    if not (in_x and in_y):
                        continue
                key = f"{person.track_id}:{product.track_id}"
                active.add(key)
                if key not in self._started:
                    self._started[key] = context.timestamp
                dwell = context.timestamp - self._started[key]
                if dwell >= min_dur:
                    out.append(
                        BehaviourEvidence(
                            behaviour=self.name,
                            start_time=self._started[key],
                            end_time=context.timestamp,
                            entities=[person.track_id, product.track_id],
                            raw_score=min(1.0, dwell / (min_dur * 2)),
                            evidence={
                                "duration_s": round(dwell, 3),
                                "person": person.track_id,
                                "product": product.track_id,
                            },
                        )
                    )
        for key in [k for k in self._started if k not in active]:
            del self._started[key]
        return out
