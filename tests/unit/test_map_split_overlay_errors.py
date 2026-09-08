from __future__ import annotations

from handleguard.metrics.detection import DetectionBox, mean_average_precision
from handleguard.metrics.error_cards import ErrorCard, classify_false_positive, error_card
from handleguard.metrics.impact import estimated_avoided_loss
from handleguard.metrics.split import ClipRecord, leakage_safe_split
from handleguard.video.overlay import OverlayBox, OverlayPlan, plan_overlay


def test_map50_perfect_match_is_one():
    preds = [DetectionBox("carton", (0, 0, 10, 10), 0.9)]
    truths = [DetectionBox("carton", (0, 0, 10, 10), 1.0)]
    result = mean_average_precision(preds, truths, iou_threshold=0.5)
    assert result.map50 == 1.0
    assert result.by_class["carton"] == 1.0


def test_map50_no_overlap_is_zero():
    preds = [DetectionBox("carton", (0, 0, 10, 10), 0.9)]
    truths = [DetectionBox("carton", (50, 50, 60, 60), 1.0)]
    result = mean_average_precision(preds, truths, iou_threshold=0.5)
    assert result.map50 == 0.0


def test_split_keeps_session_together():
    clips = [
        ClipRecord("drop_001", "session-a", "drop"),
        ClipRecord("drop_002", "session-a", "drop"),
        ClipRecord("throw_001", "session-b", "throw"),
        ClipRecord("drag_001", "session-c", "drag"),
        ClipRecord("zone_001", "session-d", "zone_violation"),
    ]
    split = leakage_safe_split(clips, train=0.4, val=0.2, test=0.4, seed=7)
    sessions = {}
    for name, group in (("train", split.train), ("val", split.val), ("test", split.test)):
        for clip in group:
            assert clip.session_id not in sessions or sessions[clip.session_id] == name
            sessions[clip.session_id] = name
    assert {c.video_id for c in split.train} | {c.video_id for c in split.val} | {
        c.video_id for c in split.test
    } == {c.video_id for c in clips}


def test_overlay_plan_includes_tracks_and_risk():
    plan = plan_overlay(
        timestamp=4.2,
        boxes=[OverlayBox("carton_8", "carton", (120, 80, 220, 170), "drop")],
        risk_score=82.0,
        behaviour="drop",
    )
    assert isinstance(plan, OverlayPlan)
    assert plan.timestamp == 4.2
    assert plan.caption.startswith("drop")
    assert "82" in plan.caption
    assert plan.boxes[0].track_id == "carton_8"
    assert "damage" not in plan.caption.lower()


def test_false_positive_error_card():
    card = error_card(
        incident_id="HG-0003",
        behaviour="drop",
        trigger="rapid downward motion",
        rejection="gentle placement onto pallet",
        signal="threshold",
    )
    assert isinstance(card, ErrorCard)
    assert card.category == "intentional_safe_handling" or classify_false_positive(
        "gentle placement onto pallet"
    ) == "intentional_safe_handling"
    assert card.incident_id == "HG-0003"
    assert "gentle" in card.why_human_rejected.lower()


def test_estimated_avoided_loss_is_labeled_assumption():
    result = estimated_avoided_loss(n_preventable=10, p_damage=0.2, cost=50.0)
    assert result.value == 100.0
    assert result.assumption_label
    assert "assumption" in result.assumption_label.lower() or "not guaranteed" in result.assumption_label.lower()
