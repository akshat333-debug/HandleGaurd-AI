from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import bbox_center, support_ratio
from handleguard.types import BehaviourEvidence, is_product


class UnstableStackDetector:
    name = "unstable_stack"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_support = float(cfg["min_support_ratio"])
        min_overlap = float(cfg.get("min_horizontal_overlap", 0.3))
        products = [t for t in context.tracks if is_product(t.class_name)]
        out: list[BehaviourEvidence] = []
        for child in products:
            for base in products:
                if child.track_id == base.track_id:
                    continue
                if bbox_center(child.bbox)[1] >= bbox_center(base.bbox)[1]:
                    continue
                ratio = support_ratio(child.bbox, base.bbox)
                if ratio >= min_overlap and ratio < min_support:
                    out.append(
                        BehaviourEvidence(
                            behaviour=self.name,
                            start_time=context.timestamp,
                            end_time=context.timestamp,
                            entities=[child.track_id, base.track_id],
                            raw_score=min(1.0, 1.0 - ratio / min_support),
                            evidence={
                                "support_ratio": round(ratio, 3),
                                "child": child.track_id,
                                "support": base.track_id,
                            },
                        )
                    )
        return out
