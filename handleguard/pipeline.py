from __future__ import annotations

from dataclasses import dataclass, field

from handleguard.behaviours.base import BehaviourContext
from handleguard.behaviours.registry import build_detectors
from handleguard.config.loader import AppConfig, load_config
from handleguard.events.graph import EventGraph, build_event_graph
from handleguard.features.zones import load_zones, resolve_zone
from handleguard.incidents.manager import IncidentEngine
from handleguard.perception.detector import Detector, StubDetector
from handleguard.perception.products import classify_product
from handleguard.pipeline_errors import EmptyDetectionsError
from handleguard.privacy.blur import blur_faces
from handleguard.tracking.passthrough import FrameLocalTracker
from handleguard.tracking.tracker import IoUTracker
from handleguard.types import Detection, Incident, TrackState, Zone


@dataclass
class PipelineResult:
    video_id: str
    tracks: list[TrackState]
    incidents: list[Incident]
    frames_processed: int


@dataclass
class HandleGuardPipeline:
    config: AppConfig
    detector: Detector
    video_id: str = "video-1"
    camera_id: str = "cam-01"
    loading_bay: str | None = "Bay-A"
    tracker: IoUTracker | FrameLocalTracker = field(default_factory=IoUTracker)
    zones: list[Zone] = field(default_factory=list)
    use_tracker: bool = True
    use_event_graph: bool = True

    def __post_init__(self) -> None:
        if not self.zones:
            self.zones = load_zones(self.config.zones)
        if not self.use_tracker:
            self.tracker = FrameLocalTracker()
        self.detectors = build_detectors()
        self.engine = IncidentEngine(self.config, video_id=self.video_id)

    @classmethod
    def from_stub(
        cls,
        timeline: list[tuple[float, list[Detection]]],
        *,
        config: AppConfig | None = None,
        video_id: str = "video-1",
        use_tracker: bool = True,
        use_event_graph: bool = True,
    ) -> "HandleGuardPipeline":
        return cls(
            config=config or load_config(),
            detector=StubDetector(timeline),
            video_id=video_id,
            use_tracker=use_tracker,
            use_event_graph=use_event_graph,
        )

    def process_frame(self, frame: object, timestamp: float, frame_height: float = 720) -> list[Incident]:
        frame = blur_faces(frame, enabled=bool(self.config.video.get("privacy", {}).get("blur_faces", True)))
        detections = self.detector.detect(frame, timestamp)
        tracks = self.tracker.update(detections, timestamp)
        for track in tracks:
            zone = resolve_zone(track.bbox, self.zones)
            track.zone = zone.name if zone else None
        if self.use_event_graph:
            graph = build_event_graph(tracks, timestamp)
        else:
            graph = EventGraph(timestamp=timestamp, tracks={t.track_id: t for t in tracks})
        context = BehaviourContext(
            timestamp=timestamp,
            tracks=tracks,
            graph=graph,
            zones=self.zones,
            config=self.config,
            extras={"frame_height": frame_height},
        )
        created: list[Incident] = []
        for detector in self.detectors:
            for evidence in detector.update(context):
                primary = evidence.entities[0] if evidence.entities else ""
                track = next((t for t in tracks if t.track_id == primary), None)
                zone = resolve_zone(track.bbox, self.zones) if track else None
                incident = self.engine.ingest(
                    evidence,
                    product_class=classify_product(track.class_name) if track else "default",
                    zone_type=zone.zone_type.value if zone else None,
                    zone_name=zone.name if zone else None,
                    camera_id=self.camera_id,
                    loading_bay=self.loading_bay,
                )
                if incident:
                    created.append(incident)
        return created

    def process_timeline(
        self,
        timestamps: list[float],
        *,
        frame_height: float = 720,
        require_detections: bool = False,
    ) -> PipelineResult:
        if timestamps:
            self.engine.video_duration = max(timestamps) + (timestamps[1] - timestamps[0] if len(timestamps) > 1 else 0.125)
        saw_detections = False
        for ts in timestamps:
            detections = self.detector.detect(None, ts)
            if detections:
                saw_detections = True
            self.process_frame(None, ts, frame_height=frame_height)
        if require_detections and not saw_detections:
            raise EmptyDetectionsError(self.video_id)
        return PipelineResult(
            video_id=self.video_id,
            tracks=self.tracker.tracks(),
            incidents=list(self.engine.incidents),
            frames_processed=len(timestamps),
        )
