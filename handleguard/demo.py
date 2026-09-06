from __future__ import annotations

from handleguard.types import Detection


def _carton(x1: float, y1: float, x2: float, y2: float, conf: float = 0.92) -> Detection:
    return Detection("carton", (x1, y1, x2, y2), conf)


def _person(x1: float, y1: float, x2: float, y2: float) -> Detection:
    return Detection("person", (x1, y1, x2, y2), 0.88)


def _pallet(x1: float, y1: float, x2: float, y2: float) -> Detection:
    return Detection("pallet", (x1, y1, x2, y2), 0.9)


def _mattress(x1: float, y1: float, x2: float, y2: float) -> Detection:
    return Detection("mattress", (x1, y1, x2, y2), 0.9)


def demo_timestamps(fps: float = 8.0, duration: float = 12.0) -> list[float]:
    n = int(duration * fps)
    return [round(i / fps, 4) for i in range(n)]


def _at(ts: float, items: list[Detection]) -> tuple[float, list[Detection]]:
    return (ts, items)


DEMO_TIMELINE: list[tuple[float, list[Detection]]] = []


def build_demo_timeline() -> list[tuple[float, list[Detection]]]:
    frames: list[tuple[float, list[Detection]]] = []
    # 0-2s drop: carton falls then stops on floor
    for i, ts in enumerate([0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5, 1.75, 2.0]):
        y = 80 + min(i, 8) * 55
        if i >= 8:
            y = 520
        frames.append(_at(ts, [_carton(120, y, 220, y + 90), _person(40, 200, 110, 520)]))
    # 2.0-3.5s throw: fast horizontal
    x = 250
    for ts in [2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3.0]:
        x += 40
        frames.append(_at(ts, [_carton(x, 240, x + 90, 330), _person(200, 180, 280, 500)]))
    # 3.5-5.5s drag near floor
    x = 80
    for ts in [3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.25, 5.5]:
        x += 30
        frames.append(_at(ts, [_carton(x, 660, x + 100, 710)]))
    # 5.5-7s zone violation in walkway / restricted
    for ts in [5.625, 5.75, 6.0, 6.25, 6.5, 6.75, 7.0, 7.25, 7.5, 7.75, 8.0]:
        frames.append(_at(ts, [_carton(40, 520, 140, 620)]))
    # 8-9s pallet overhang
    frames.append(_at(8.125, [_pallet(400, 500, 700, 700), _carton(360, 430, 760, 620)]))
    frames.append(_at(8.25, [_pallet(400, 500, 700, 700), _carton(360, 430, 760, 620)]))
    frames.append(_at(8.5, [_pallet(400, 500, 700, 700), _carton(360, 430, 760, 620)]))
    # 9-10s improper + unstable stack
    frames.append(
        _at(
            9.0,
            [
                _carton(500, 480, 620, 600),
                _carton(520, 300, 700, 470),
            ],
        )
    )
    frames.append(
        _at(
            9.25,
            [
                _carton(500, 480, 620, 600),
                _carton(520, 300, 700, 470),
            ],
        )
    )
    # 10-11s stepping
    for ts in [10.0, 10.25, 10.5, 10.75, 11.0]:
        frames.append(
            _at(
                ts,
                [
                    _carton(200, 400, 360, 560),
                    _person(230, 250, 320, 480),
                ],
            )
        )
    # 11-12s large mattress moved without equipment (manual + sequence)
    x = 600
    for ts in [11.125, 11.25, 11.375, 11.5, 11.625, 11.75, 11.875]:
        x += 18
        frames.append(
            _at(
                ts,
                [
                    _mattress(x, 200, x + 220, 420),
                    _person(x - 40, 180, x + 20, 500),
                ],
            )
        )
    # wet floor movement
    x = 220
    for ts in [4.1, 4.4, 4.7, 5.1]:
        x += 20
        frames.append(_at(ts, [_carton(x, 560, x + 80, 650)]))
    return frames


DEMO_TIMELINE = build_demo_timeline()
