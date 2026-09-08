from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BehaviourCard:
    name: str
    detects: str
    does_not_detect: str
    failure_conditions: str
    camera_view: str
    minimum_visibility: str
    calibration_status: str


_CARDS: dict[str, BehaviourCard] = {
    "drop": BehaviourCard(
        name="drop",
        detects="Rapid downward product motion followed by an abrupt stop / impact.",
        does_not_detect="Gentle placement, camera jitter, or slow lowering onto a pallet.",
        failure_conditions="Occlusion at impact, extreme fisheye, or unstable camera.",
        camera_view="Fixed side or three-quarter view of the loading bay with floor visible.",
        minimum_visibility="Product bbox visible for at least 3 sampled frames during the fall.",
        calibration_status="image-space",
    ),
    "throw": BehaviourCard(
        name="throw",
        detects="High unsupported horizontal velocity after leaving a handler.",
        does_not_detect="Carried motion with a nearby person track.",
        failure_conditions="Missed person detections make carry look unsupported.",
        camera_view="Side view covering handler and flight path.",
        minimum_visibility="Product visible across at least 2 consecutive inference frames.",
        calibration_status="image-space",
    ),
    "drag": BehaviourCard(
        name="drag",
        detects="Sustained floor-level horizontal translation of a product.",
        does_not_detect="Lifted carry above the floor proximity band.",
        failure_conditions="Floor line not visible; perspective foreshortening.",
        camera_view="Floor and pallet edges in frame.",
        minimum_visibility="Product bottom edge visible for the configured duration.",
        calibration_status="image-space",
    ),
}


def behaviour_card(name: str) -> BehaviourCard:
    if name in _CARDS:
        return _CARDS[name]
    return BehaviourCard(
        name=name,
        detects=f"Configured {name.replace('_', ' ')} pattern from YAML thresholds.",
        does_not_detect="Transient noise below the YAML duration/intensity thresholds.",
        failure_conditions="Poor lighting, occlusion, or zone polygons that do not match the camera.",
        camera_view="Fixed 720p view of the loading area.",
        minimum_visibility="Primary object visible for the detector cooldown window.",
        calibration_status="uncalibrated",
    )
