from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.types import BehaviourEvidence, is_equipment, is_product


class UnsafeSequenceDetector:
    """Flags lift/move of a large product before equipment is present."""

    name = "unsafe_sequence"

    def __init__(self) -> None:
        self._saw_equipment = False

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        if any(is_equipment(t.class_name) for t in context.tracks):
            self._saw_equipment = True
        out: list[BehaviourEvidence] = []
        if self._saw_equipment:
            return out
        for product in context.tracks:
            if not is_product(product.class_name):
                continue
            meta = context.config.product_meta(product.class_name)
            moving = abs(product.velocity[0]) + abs(product.velocity[1]) > 40
            if meta.get("large") and moving:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=context.timestamp,
                        end_time=context.timestamp,
                        entities=[product.track_id],
                        raw_score=0.65,
                        evidence={"reason": "large_product_moved_without_equipment"},
                    )
                )
        return out
