from __future__ import annotations

from handleguard.types import HistoryEntry, Point


def exponential_smooth(previous: float, current: float, alpha: float = 0.4) -> float:
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in (0, 1]")
    return alpha * current + (1.0 - alpha) * previous


def kinematics_from_history(
    history: list[HistoryEntry],
    alpha: float = 0.4,
) -> tuple[Point, Point]:
    """Return smoothed (velocity, acceleration) from track history.

    Velocity uses image coordinates (y increases downward).
    Requires at least two samples; otherwise returns zeros.
    """
    if len(history) < 2:
        return (0.0, 0.0), (0.0, 0.0)

    vx = 0.0
    vy = 0.0
    ax = 0.0
    ay = 0.0
    prev_vx: float | None = None
    prev_vy: float | None = None

    for prev, curr in zip(history, history[1:]):
        dt = curr.timestamp - prev.timestamp
        if dt <= 0:
            continue
        raw_vx = (curr.center[0] - prev.center[0]) / dt
        raw_vy = (curr.center[1] - prev.center[1]) / dt
        vx = exponential_smooth(vx, raw_vx, alpha) if prev_vx is not None else raw_vx
        vy = exponential_smooth(vy, raw_vy, alpha) if prev_vy is not None else raw_vy
        if prev_vx is not None and prev_vy is not None:
            raw_ax = (vx - prev_vx) / dt
            raw_ay = (vy - prev_vy) / dt
            ax = exponential_smooth(ax, raw_ax, alpha)
            ay = exponential_smooth(ay, raw_ay, alpha)
        prev_vx, prev_vy = vx, vy

    return (vx, vy), (ax, ay)
