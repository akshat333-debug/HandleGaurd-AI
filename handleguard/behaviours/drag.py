from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.features.geometry import bbox_bottom_center
from handleguard.types import BehaviourEvidence, is_product


class DragDetector:
    name = "drag"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_dist = float(cfg["min_distance_pixels"])
        max_vert = float(cfg["max_vertical_variation"])
        min_dur = float(cfg["min_duration_seconds"])
        floor_px = float(cfg.get("floor_proximity_px", 30))
        frame_h = float(context.extras.get("frame_height", 720))
        out: list[BehaviourEvidence] = []
        for track in context.tracks:
            if not is_product(track.class_name) or len(track.history) < 3:
                continue
            duration = track.last_seen - track.history[0].timestamp
            if duration < min_dur:
                continue
            bottoms = [bbox_bottom_center(h.bbox)[1] for h in track.history]
            xs = [h.center[0] for h in track.history]
            vert = max(bottoms) - min(bottoms)
            horiz = abs(xs[-1] - xs[0])
            near_floor = min(abs(frame_h - b) for b in bottoms) <= floor_px or min(bottoms) >= frame_h - floor_px * 3
            if horiz >= min_dist and vert <= max_vert and near_floor:
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=track.history[0].timestamp,
                        end_time=track.last_seen,
                        entities=[track.track_id],
                        raw_score=min(1.0, horiz / (min_dist * 1.5)),
                        evidence={
                            "distance_px": round(horiz, 2),
                            "vertical_variation_px": round(vert, 2),
                            "duration_s": round(duration, 3),
                        },
                    )
                )
        return out
