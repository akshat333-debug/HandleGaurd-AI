from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.types import BehaviourEvidence, is_product


class ThrowDetector:
    name = "throw"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_vx = float(cfg["min_horizontal_velocity"])
        min_frames = int(cfg["min_unsupported_frames"])
        out: list[BehaviourEvidence] = []
        for track in context.tracks:
            if not is_product(track.class_name) or len(track.history) < min_frames + 1:
                continue
            vx = abs(track.velocity[0])
            vy = track.velocity[1]
            if vx < min_vx:
                continue
            if vx <= abs(vy) * 0.85:
                continue
            associated = bool(context.graph.related(track.track_id, "handling"))
            out.append(
                BehaviourEvidence(
                    behaviour=self.name,
                    start_time=track.history[-min_frames].timestamp,
                    end_time=track.last_seen,
                    entities=[track.track_id],
                    raw_score=min(1.0, vx / (min_vx * 1.4)),
                    evidence={
                        "horizontal_velocity": round(vx, 2),
                        "vertical_velocity": round(vy, 2),
                        "person_associated": associated,
                    },
                )
            )
        return out
