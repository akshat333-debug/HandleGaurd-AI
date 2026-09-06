from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import bbox_area, bbox_center, distance
from handleguard.types import BehaviourEvidence, is_equipment, is_person, is_product


class ImproperManualHandlingDetector:
    name = "improper_manual_handling"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        large_area = float(cfg["large_area_px"])
        max_people = int(cfg["max_nearby_people"])
        equip_px = float(cfg["equipment_proximity_px"])
        people = [t for t in context.tracks if is_person(t.class_name)]
        equipment = [t for t in context.tracks if is_equipment(t.class_name)]
        out: list[BehaviourEvidence] = []
        for product in context.tracks:
            if not is_product(product.class_name):
                continue
            meta = context.config.product_meta(product.class_name)
            large = bool(meta.get("large")) or bbox_area(product.bbox) >= large_area
            if not large:
                continue
            nearby_people = [
                p
                for p in people
                if distance(bbox_center(p.bbox), bbox_center(product.bbox)) <= equip_px
            ]
            nearby_eq = [
                e
                for e in equipment
                if distance(bbox_center(e.bbox), bbox_center(product.bbox)) <= equip_px
            ]
            moving = abs(product.velocity[0]) + abs(product.velocity[1]) > 20
            if moving and len(nearby_people) <= max_people and not nearby_eq:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=context.timestamp,
                        end_time=context.timestamp,
                        entities=[product.track_id] + [p.track_id for p in nearby_people],
                        raw_score=0.7,
                        evidence={
                            "nearby_people": len(nearby_people),
                            "equipment_nearby": False,
                            "area_px": round(bbox_area(product.bbox), 1),
                        },
                    )
                )
        return out
