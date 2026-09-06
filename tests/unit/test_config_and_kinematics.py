from __future__ import annotations

import pytest

from handleguard.config.loader import load_config
from handleguard.features.kinematics import exponential_smooth, kinematics_from_history
from handleguard.types import HistoryEntry


def test_load_config_contains_twelve_behaviours():
    cfg = load_config()
    names = [
        "drop",
        "throw",
        "drag",
        "rough_handling",
        "improper_stack",
        "unstable_stack",
        "zone_violation",
        "pallet_overhang",
        "stepping",
        "improper_manual_handling",
        "unsafe_sequence",
        "unsafe_surface",
    ]
    for name in names:
        assert cfg.behaviour(name)["enabled"] is True


def test_unknown_behaviour_raises():
    cfg = load_config()
    with pytest.raises(KeyError):
        cfg.behaviour("not_a_behaviour")


def test_product_meta_fallback_default():
    cfg = load_config()
    meta = cfg.product_meta("unknown-sku")
    assert meta["fragility"] == 0.4


def test_exponential_smooth():
    assert exponential_smooth(0.0, 10.0, 0.5) == 5.0


def test_exponential_smooth_rejects_bad_alpha():
    with pytest.raises(ValueError):
        exponential_smooth(0.0, 1.0, 0.0)


def test_kinematics_from_two_points():
    history = [
        HistoryEntry(0.0, (0, 0, 10, 10), (5, 5), 10, 10, 0.9),
        HistoryEntry(1.0, (0, 10, 10, 20), (5, 15), 10, 10, 0.9),
    ]
    vel, _acc = kinematics_from_history(history, alpha=1.0)
    assert vel == (0.0, 10.0)


def test_kinematics_empty_history_is_zero():
    assert kinematics_from_history([]) == ((0.0, 0.0), (0.0, 0.0))
