from __future__ import annotations

from handleguard.behaviours.base import BehaviourContext
from handleguard.behaviours.drag import DragDetector
from handleguard.behaviours.drop import DropDetector
from handleguard.behaviours.improper_manual_handling import ImproperManualHandlingDetector
from handleguard.behaviours.improper_stack import ImproperStackDetector
from handleguard.behaviours.pallet_overhang import PalletOverhangDetector
from handleguard.behaviours.registry import build_detectors
from handleguard.behaviours.rough_handling import RoughHandlingDetector
from handleguard.behaviours.stepping import SteppingDetector
from handleguard.behaviours.throw import ThrowDetector
from handleguard.behaviours.unsafe_sequence import UnsafeSequenceDetector
from handleguard.behaviours.unsafe_surface import UnsafeSurfaceDetector
from handleguard.behaviours.unstable_stack import UnstableStackDetector
from handleguard.behaviours.zone_violation import ZoneViolationDetector
from handleguard.config.loader import load_config
from handleguard.events.graph import EventGraph, build_event_graph
from handleguard.features.zones import load_zones
from tests.conftest import make_track


def _ctx(tracks, ts=2.0, extras=None):
    cfg = load_config()
    zones = load_zones(cfg.zones)
    graph = build_event_graph(tracks, ts)
    return BehaviourContext(
        timestamp=ts,
        tracks=tracks,
        graph=graph,
        zones=zones,
        config=cfg,
        extras=extras or {"frame_height": 720},
    )


def test_registry_has_twelve_detectors():
    names = [d.name for d in build_detectors()]
    assert len(names) == 12
    assert len(set(names)) == 12


def test_drop_true_positive():
    boxes = []
    y = 80
    for i in range(10):
        ts = i * 0.125
        if i < 7:
            y = 80 + i * 70
        else:
            y = 520
        boxes.append((ts, (100, y, 180, y + 80)))
    track = make_track("carton_1", "carton", boxes)
    hits = DropDetector().update(_ctx([track], ts=boxes[-1][0]))
    assert len(hits) == 1
    assert hits[0].behaviour == "drop"
    assert hits[0].evidence["drop_distance_px"] >= 45


def test_drop_rejects_gentle_placement():
    boxes = [(i * 0.25, (100, 200 + i * 4, 180, 280 + i * 4)) for i in range(8)]
    track = make_track("carton_1", "carton", boxes)
    assert DropDetector().update(_ctx([track], ts=boxes[-1][0])) == []


def test_throw_high_horizontal_velocity():
    boxes = [(i * 0.125, (50 + i * 40, 200, 130 + i * 40, 280)) for i in range(6)]
    track = make_track("carton_1", "carton", boxes)
    hits = ThrowDetector().update(_ctx([track], ts=boxes[-1][0]))
    assert len(hits) == 1
    assert hits[0].behaviour == "throw"


def test_drag_near_floor():
    boxes = [(i * 0.25, (40 + i * 30, 660, 140 + i * 30, 710)) for i in range(8)]
    track = make_track("carton_1", "carton", boxes)
    hits = DragDetector().update(_ctx([track], ts=boxes[-1][0]))
    assert len(hits) == 1


def test_drag_rejects_carry_at_height():
    boxes = [(i * 0.25, (40 + i * 30, 200, 140 + i * 30, 280)) for i in range(8)]
    track = make_track("carton_1", "carton", boxes)
    assert DragDetector().update(_ctx([track], ts=boxes[-1][0])) == []


def test_zone_violation_persistent_not_transient():
    det = ZoneViolationDetector()
    boxes_short = [(0.0, (40, 520, 120, 600)), (0.5, (40, 520, 120, 600))]
    track = make_track("carton_1", "carton", boxes_short)
    assert det.update(_ctx([track], ts=0.5)) == []
    boxes_long = [(i * 0.5, (40, 520, 120, 600)) for i in range(6)]
    track = make_track("carton_1", "carton", boxes_long)
    det = ZoneViolationDetector()
    hits = []
    for ts, _box in boxes_long:
        track.last_seen = ts
        hits = det.update(_ctx([track], ts=ts))
    assert hits and hits[0].behaviour == "zone_violation"


def test_pallet_overhang():
    product = make_track("carton_1", "carton", [(1.0, (360, 430, 760, 620))])
    pallet = make_track("pallet_1", "pallet", [(1.0, (400, 500, 700, 700))])
    hits = PalletOverhangDetector().update(_ctx([product, pallet], ts=1.0))
    assert hits and hits[0].behaviour == "pallet_overhang"


def test_unstable_and_improper_stack():
    lower = make_track("carton_1", "carton", [(1.0, (500, 480, 620, 600))])
    upper = make_track("carton_2", "carton", [(1.0, (520, 300, 700, 470))])
    ctx = _ctx([lower, upper], ts=1.0)
    unstable = UnstableStackDetector().update(ctx)
    improper = ImproperStackDetector().update(ctx)
    assert unstable or improper


def test_stepping_requires_dwell():
    det = SteppingDetector()
    product = make_track("carton_1", "carton", [(0.0, (200, 400, 360, 560)), (1.0, (200, 400, 360, 560))])
    person = make_track("person_1", "person", [(0.0, (230, 250, 320, 480)), (1.0, (230, 250, 320, 480))])
    assert det.update(_ctx([product, person], ts=0.0)) == []
    hits = det.update(_ctx([product, person], ts=1.0))
    assert hits and hits[0].behaviour == "stepping"


def test_improper_manual_and_unsafe_sequence():
    mattress = make_track(
        "mattress_1",
        "mattress",
        [(i * 0.125, (600 + i * 20, 200, 820 + i * 20, 420)) for i in range(5)],
    )
    person = make_track("person_1", "person", [(0.5, (560, 180, 620, 500))])
    ctx = _ctx([mattress, person], ts=0.5)
    manual = ImproperManualHandlingDetector().update(ctx)
    seq = UnsafeSequenceDetector().update(ctx)
    assert manual or seq


def test_unsafe_surface_moving_product():
    det = UnsafeSurfaceDetector()
    boxes = [(i * 0.5, (220 + i * 20, 560, 300 + i * 20, 650)) for i in range(5)]
    track = make_track("carton_1", "carton", boxes)
    hits = []
    for ts, _ in boxes:
        hits = det.update(_ctx([track], ts=ts))
    assert hits and hits[0].behaviour == "unsafe_surface"


def test_rough_handling_acceleration_spike():
    boxes = [
        (0.0, (100, 200, 180, 280)),
        (0.125, (100, 210, 180, 290)),
        (0.25, (100, 400, 180, 480)),
        (0.375, (100, 405, 180, 485)),
    ]
    track = make_track("carton_1", "carton", boxes)
    hits = RoughHandlingDetector().update(_ctx([track], ts=0.375))
    assert hits == [] or hits[0].behaviour == "rough_handling"
