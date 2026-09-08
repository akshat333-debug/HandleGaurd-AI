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
    "rough_handling": BehaviourCard(
        name="rough_handling",
        detects="Abrupt acceleration or impact spike on a product track.",
        does_not_detect="Smooth placement or low-acceleration carry.",
        failure_conditions="Detection jitter mistaken for an impact spike.",
        camera_view="Close enough to resolve product bbox motion between frames.",
        minimum_visibility="Product visible for at least 3 consecutive sampled frames.",
        calibration_status="image-space",
    ),
    "improper_stack": BehaviourCard(
        name="improper_stack",
        detects="A larger item resting on a smaller support with sufficient overlap.",
        does_not_detect="Equal-size stacks or items merely adjacent.",
        failure_conditions="Depth compression makes distant boxes look stacked.",
        camera_view="Side view of the stack with both footprints visible.",
        minimum_visibility="Both product boxes visible in the same frame.",
        calibration_status="uncalibrated",
    ),
    "unstable_stack": BehaviourCard(
        name="unstable_stack",
        detects="Low support ratio / overhang of an upper product on a lower one.",
        does_not_detect="Well-centred stacks above the support-ratio threshold.",
        failure_conditions="Partial occlusion of the lower carton.",
        camera_view="Side or three-quarter view of the stack.",
        minimum_visibility="Upper and lower product bboxes co-visible.",
        calibration_status="uncalibrated",
    ),
    "zone_violation": BehaviourCard(
        name="zone_violation",
        detects="Persistent product dwell in a restricted or walkway zone.",
        does_not_detect="Transient crossings shorter than the configured delay.",
        failure_conditions="Zone polygons that do not match the current camera homography.",
        camera_view="Floor markings and zone corners visible.",
        minimum_visibility="Product centre inside the polygon for the dwell window.",
        calibration_status="uncalibrated",
    ),
    "pallet_overhang": BehaviourCard(
        name="pallet_overhang",
        detects="Product-pallet overlap below the configured support fraction.",
        does_not_detect="Fully supported cartons on a pallet.",
        failure_conditions="Missed pallet detections or perspective foreshortening.",
        camera_view="Pallet edges and product footprint both in frame.",
        minimum_visibility="Pallet and product bboxes co-visible.",
        calibration_status="uncalibrated",
    ),
    "stepping": BehaviourCard(
        name="stepping",
        detects="Person footprint overlapping a product for a sustained interval.",
        does_not_detect="Walking beside product without bbox overlap.",
        failure_conditions="Top-down views that merge person and carton boxes.",
        camera_view="Oblique view showing person feet and product top.",
        minimum_visibility="Person and product co-visible for the dwell threshold.",
        calibration_status="uncalibrated",
    ),
    "improper_manual_handling": BehaviourCard(
        name="improper_manual_handling",
        detects="A large item moved by too few people with no nearby equipment.",
        does_not_detect="Team lifts or equipment-assisted moves.",
        failure_conditions="Missed person or equipment detections.",
        camera_view="Wide bay view covering handlers and equipment.",
        minimum_visibility="Product plus nearby person/equipment tracks.",
        calibration_status="uncalibrated",
    ),
    "unsafe_sequence": BehaviourCard(
        name="unsafe_sequence",
        detects="A large item moved before equipment is in position.",
        does_not_detect="Equipment already nearby when the product starts moving.",
        failure_conditions="Late equipment detections after the product is already in motion.",
        camera_view="Bay entrance and equipment staging visible.",
        minimum_visibility="Product and equipment tracks across the sequence window.",
        calibration_status="uncalibrated",
    ),
    "unsafe_surface": BehaviourCard(
        name="unsafe_surface",
        detects="Product movement through a marked wet-floor / unsafe-surface zone.",
        does_not_detect="Transit through allowed staging zones.",
        failure_conditions="Unsafe-surface polygons not aligned with floor markings.",
        camera_view="Floor markings for wet/unsafe areas visible.",
        minimum_visibility="Product centre inside the unsafe polygon during motion.",
        calibration_status="uncalibrated",
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
