from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import bbox_area, bbox_center, horizontal_overlap
from handleguard.types import BehaviourEvidence, is_product


class ImproperStackDetector:
    name = "improper_stack"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_overlap = float(cfg["min_horizontal_overlap"])
        size_ratio = float(cfg["size_ratio"])
        products = [t for t in context.tracks if is_product(t.class_name)]
        out: list[BehaviourEvidence] = []
        for upper in products:
            for lower in products:
                if upper.track_id == lower.track_id:
                    continue
                if bbox_center(upper.bbox)[1] >= bbox_center(lower.bbox)[1]:
                    continue
                overlap = horizontal_overlap(upper.bbox, lower.bbox)
                if overlap < min_overlap:
                    continue
                upper_area = bbox_area(upper.bbox)
                lower_area = bbox_area(lower.bbox)
                if lower_area <= 0 or upper_area < lower_area * size_ratio:
                    continue
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=context.timestamp,
                        end_time=context.timestamp,
                        entities=[upper.track_id, lower.track_id],
                        raw_score=min(1.0, overlap * (upper_area / lower_area) / 2),
                        evidence={
                            "overlap": round(overlap, 3),
                            "size_ratio": round(upper_area / lower_area, 3),
                            "upper": upper.track_id,
                            "lower": lower.track_id,
                        },
                    )
                )
        return out
