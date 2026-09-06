from __future__ import annotations

from math import hypot

from handleguard.behaviours.base import BehaviourContext
from handleguard.types import BehaviourEvidence, is_product


class RoughHandlingDetector:
    name = "rough_handling"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_acc = float(cfg["min_acceleration"])
        min_dec = float(cfg["min_deceleration"])
        out: list[BehaviourEvidence] = []
        for track in context.tracks:
            if not is_product(track.class_name) or len(track.history) < 3:
                continue
            acc_mag = hypot(*track.acceleration)
            if acc_mag < min_acc and abs(track.acceleration[1]) < min_dec:
                continue
            out.append(
                BehaviourEvidence(
                    behaviour=self.name,
                    start_time=max(track.first_seen, track.last_seen - 0.5),
                    end_time=track.last_seen,
                    entities=[track.track_id],
                    raw_score=min(1.0, acc_mag / (min_acc * 1.5)),
                    evidence={
                        "acceleration": round(acc_mag, 2),
                        "ay": round(track.acceleration[1], 2),
                    },
                )
            )
        return out
