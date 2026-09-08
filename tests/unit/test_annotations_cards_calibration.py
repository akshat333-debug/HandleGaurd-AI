from __future__ import annotations

from handleguard.perception.products import classify_product
from handleguard.risk.calibration import describe_drop, pixels_to_metres
from handleguard.video.annotations import BehaviourEvent, parse_annotation, serialize_annotation
from handleguard.behaviours.cards import behaviour_card


def test_parse_annotation_json():
    payload = {
        "video_id": "drop_014",
        "events": [
            {
                "behaviour": "drop",
                "start_s": 4.20,
                "end_s": 5.75,
                "actor_track": "person_2",
                "object_track": "carton_7",
                "risk": "high",
            }
        ],
    }
    record = parse_annotation(payload)
    assert record.video_id == "drop_014"
    assert len(record.events) == 1
    event = record.events[0]
    assert isinstance(event, BehaviourEvent)
    assert event.behaviour == "drop"
    assert event.start_s == 4.20
    assert event.object_track == "carton_7"


def test_serialize_annotation_roundtrip():
    payload = {
        "video_id": "throw_001",
        "events": [
            {
                "behaviour": "throw",
                "start_s": 1.0,
                "end_s": 2.0,
                "actor_track": "person_1",
                "object_track": "carton_1",
                "risk": "critical",
            }
        ],
    }
    record = parse_annotation(payload)
    dumped = serialize_annotation(record)
    assert dumped["video_id"] == "throw_001"
    assert dumped["events"][0]["behaviour"] == "throw"


def test_behaviour_card_has_required_fields():
    card = behaviour_card("drop")
    assert "rapid downward" in card.detects.lower() or "drop" in card.detects.lower()
    assert "gentle" in card.does_not_detect.lower()
    assert card.camera_view
    assert card.calibration_status in {"image-space", "uncalibrated", "calibrated"}
    assert card.minimum_visibility


def test_classify_product_aliases():
    assert classify_product("box") == "carton"
    assert classify_product("fragile_package") == "electronics"
    assert classify_product("pallet_truck") == "pallet_jack"
    assert classify_product("unknown_widget") == "default"


def test_uncalibrated_drop_uses_pixel_proxy():
    text = describe_drop(91.0, metres_per_pixel=None)
    assert "91" in text
    assert "px" in text.lower() or "pixel" in text.lower()
    assert "metre" not in text.lower() and "meter" not in text.lower()


def test_calibrated_drop_is_labelled_estimate():
    metres = pixels_to_metres(91.0, metres_per_pixel=0.011)
    assert abs(metres - 1.001) < 0.02
    text = describe_drop(91.0, metres_per_pixel=0.011)
    assert "1" in text
    assert "calibrated" in text.lower()
    assert "1.00 metre drop" not in text.lower()
