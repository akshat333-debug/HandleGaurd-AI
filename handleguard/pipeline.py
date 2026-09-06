from __future__ import annotations

from dataclasses import dataclass, field

from handleguard.behaviours.base import BehaviourContext
from handleguard.behaviours.registry import build_detectors
from handleguard.config.loader import AppConfig, load_config
from handleguard.events.graph import build_event_graph
from handleguard.features.zones import load_zones, resolve_zone
from handleguard.incidents.manager import IncidentEngine
from handleguard.perception.detector import Detector, StubDetector
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
    tracker: IoUTracker = field(default_factory=IoUTracker)
    zones: list[Zone] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.zones:
            self.zones = load_zones(self.config.zones)
        self.detectors = build_detectors()
        self.engine = IncidentEngine(self.config, video_id=self.video_id)

    @classmethod
    def from_stub(
        cls,
        timeline: list[tuple[float, list[Detection]]],
        *,
        config: AppConfig | None = None,
        video_id: str = "video-1",
    ) -> "HandleGuardPipeline":
        return cls(
            config=config or load_config(),
            detector=StubDetector(timeline),
            video_id=video_id,
        )

    def process_frame(self, frame: object, timestamp: float, frame_height: float = 720) -> list[Incident]:
        detections = self.detector.detect(frame, timestamp)
        tracks = self.tracker.update(detections, timestamp)
        for track in tracks:
            zone = resolve_zone(track.bbox, self.zones)
            track.zone = zone.name if zone else None
        graph = build_event_graph(tracks, timestamp)
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
                    product_class=track.class_name if track else "default",
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
    ) -> PipelineResult:
        for ts in timestamps:
            self.process_frame(None, ts, frame_height=frame_height)
        return PipelineResult(
            video_id=self.video_id,
            tracks=self.tracker.tracks(),
            incidents=list(self.engine.incidents),
            frames_processed=len(timestamps),
        )
