from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import support_fraction
from handleguard.types import BehaviourEvidence, is_pallet, is_product


class PalletOverhangDetector:
    name = "pallet_overhang"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_support = float(cfg["min_support_fraction"])
        products = [t for t in context.tracks if is_product(t.class_name) and not is_pallet(t.class_name)]
        pallets = [t for t in context.tracks if is_pallet(t.class_name)]
        out: list[BehaviourEvidence] = []
        for product in products:
            best = None
            best_frac = 0.0
            for pallet in pallets:
                frac = support_fraction(product.bbox, pallet.bbox)
                if frac > best_frac:
                    best_frac = frac
                    best = pallet
            if best is None:
                continue
            if 0.05 < best_frac < min_support:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=context.timestamp,
                        end_time=context.timestamp,
                        entities=[product.track_id, best.track_id],
                        raw_score=min(1.0, 1.0 - best_frac / min_support),
                        evidence={
                            "support_fraction": round(best_frac, 3),
                            "product": product.track_id,
                            "pallet": best.track_id,
                        },
                    )
                )
        return out
