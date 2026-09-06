from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.types import BehaviourEvidence, is_product


class DropDetector:
    name = "drop"

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        cfg = context.config.behaviour(self.name)
        if not cfg.get("enabled", True):
            return []
        min_fall = float(cfg["min_fall_pixels"])
        min_vy = float(cfg["min_downward_velocity"])
        min_dec = float(cfg["impact_deceleration"])
        out: list[BehaviourEvidence] = []
        for track in context.tracks:
            if not is_product(track.class_name) or len(track.history) < 3:
                continue
            start = track.history[0]
            peak = max(track.history, key=lambda h: h.center[1])
            fall = peak.center[1] - min(h.center[1] for h in track.history)
            speeds = []
            for prev, curr in zip(track.history, track.history[1:]):
                dt = curr.timestamp - prev.timestamp
                if dt > 0:
                    speeds.append((curr.center[1] - prev.center[1]) / dt)
            peak_speed = max(speeds) if speeds else track.velocity[1]
            vy = track.velocity[1]
            ay = track.acceleration[1]
            stopped = abs(vy) < min_vy * 0.35
            had_fall_speed = peak_speed >= min_vy
            impact = (ay < 0 and abs(ay) >= min_dec) or (had_fall_speed and stopped)
            falling = fall >= min_fall and had_fall_speed
            if falling and impact:
                duration = max(0.05, peak.timestamp - start.timestamp)
                score = min(1.0, (fall / min_fall) * 0.5 + min(1.0, peak_speed / max(min_vy, 1)) * 0.5)
                out.append(
                    BehaviourEvidence(
                        behaviour=self.name,
                        start_time=start.timestamp,
                        end_time=track.last_seen,
                        entities=[track.track_id],
                        raw_score=score,
                        evidence={
                            "drop_distance_px": round(fall, 2),
                            "peak_speed": round(peak_speed, 2),
                            "impact_deceleration": round(abs(ay), 2),
                            "duration_s": round(duration, 3),
                        },
                    )
                )
        return out
