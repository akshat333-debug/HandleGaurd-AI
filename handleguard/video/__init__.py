from handleguard.video.annotations import AnnotationRecord, BehaviourEvent, parse_annotation, serialize_annotation
from handleguard.video.camera import CameraGuidance, camera_guidance
from handleguard.video.clip_writer import write_clip_sidecar
from handleguard.video.overlay import OverlayBox, OverlayPlan, plan_overlay
from handleguard.video.reader import VideoSource
from handleguard.video.sampler import sample_timestamps
from handleguard.video.stream import WebcamSource

__all__ = [
    "AnnotationRecord",
    "BehaviourEvent",
    "CameraGuidance",
    "OverlayBox",
    "OverlayPlan",
    "VideoSource",
    "WebcamSource",
    "camera_guidance",
    "parse_annotation",
    "plan_overlay",
    "sample_timestamps",
    "serialize_annotation",
    "write_clip_sidecar",
]
