from __future__ import annotations

from typing import Any


def demo_annotation_pack() -> dict[str, Any]:
    return {
        "video_id": "demo",
        "events": [
            {"behaviour": "drop", "start_s": 0.5, "end_s": 2.0, "actor_track": "person_1", "object_track": "carton_1", "risk": "high"},
            {"behaviour": "throw", "start_s": 2.1, "end_s": 3.1, "actor_track": "person_1", "object_track": "carton_2", "risk": "critical"},
            {"behaviour": "drag", "start_s": 3.5, "end_s": 5.5, "actor_track": None, "object_track": "carton_3", "risk": "medium"},
            {"behaviour": "unsafe_surface", "start_s": 4.1, "end_s": 5.1, "actor_track": None, "object_track": "carton_4", "risk": "medium"},
            {"behaviour": "zone_violation", "start_s": 5.6, "end_s": 8.0, "actor_track": None, "object_track": "carton_5", "risk": "high"},
            {"behaviour": "pallet_overhang", "start_s": 8.1, "end_s": 8.6, "actor_track": None, "object_track": "carton_6", "risk": "medium"},
            {"behaviour": "improper_stack", "start_s": 9.0, "end_s": 9.4, "actor_track": None, "object_track": "carton_7", "risk": "high"},
            {"behaviour": "unstable_stack", "start_s": 9.0, "end_s": 9.4, "actor_track": None, "object_track": "carton_8", "risk": "high"},
            {"behaviour": "stepping", "start_s": 10.0, "end_s": 11.0, "actor_track": "person_2", "object_track": "carton_9", "risk": "critical"},
            {"behaviour": "improper_manual_handling", "start_s": 11.1, "end_s": 11.9, "actor_track": "person_3", "object_track": "mattress_1", "risk": "high"},
            {"behaviour": "unsafe_sequence", "start_s": 11.1, "end_s": 11.9, "actor_track": "person_3", "object_track": "mattress_1", "risk": "high"},
        ],
    }


DEMO_ANNOTATIONS = demo_annotation_pack()


def demo_clip_catalog() -> list[dict[str, Any]]:
    clips = [
        ("01_drop.mp4", "drop"),
        ("02_drag.mp4", "drag"),
        ("03_throw.mp4", "throw"),
        ("04_bad_stack.mp4", "improper_stack"),
        ("05_unstable_stack.mp4", "unstable_stack"),
        ("06_zone_violation.mp4", "zone_violation"),
        ("07_pallet_overhang.mp4", "pallet_overhang"),
        ("08_step_on_box.mp4", "stepping"),
        ("09_manual_heavy_lift.mp4", "improper_manual_handling"),
        ("10_unsafe_sequence.mp4", "unsafe_sequence"),
        ("11_normal_handling.mp4", "negative"),
        ("12_mixed_shift.mp4", "mixed"),
    ]
    return [
        {
            "filename": name,
            "behaviour": behaviour,
            "offline": True,
            "path": f"demo/{name}",
        }
        for name, behaviour in clips
    ]

