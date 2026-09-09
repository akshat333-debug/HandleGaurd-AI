from __future__ import annotations

from handleguard.assistant.service import AssistantService
from handleguard.config.loader import load_config
from handleguard.demo_pack import demo_clip_catalog
from handleguard.pipeline import HandleGuardPipeline
from handleguard.types import Detection, Incident, IncidentStatus, RiskLevel
from handleguard.video.preprocess import FrameSize, resize_frame


def test_resize_frame_downscales_to_max_resolution():
    size = resize_frame(width=1920, height=1080, max_resolution=(1280, 720))
    assert isinstance(size, FrameSize)
    assert size.width <= 1280
    assert size.height <= 720
    assert abs(size.width / size.height - 1920 / 1080) < 0.02


def test_resize_frame_keeps_smaller_input():
    size = resize_frame(width=640, height=360, max_resolution=(1280, 720))
    assert size.width == 640
    assert size.height == 360


def test_negative_gentle_timeline_has_no_critical_drop():
    timeline = []
    for i in range(16):
        ts = i * 0.25
        y = 180 + i * 2
        timeline.append((ts, [Detection("carton", (100, y, 180, y + 80), 0.9)]))
    result = HandleGuardPipeline.from_stub(timeline, config=load_config(), video_id="neg-gentle").process_timeline(
        [t[0] for t in timeline]
    )
    critical_drops = [i for i in result.incidents if i.behaviour == "drop" and i.risk_level.value == "Critical"]
    assert critical_drops == []


def test_demo_clip_catalog_lists_twelve_offline_clips():
    catalog = demo_clip_catalog()
    names = [item["filename"] for item in catalog]
    assert "01_drop.mp4" in names
    assert "11_normal_handling.mp4" in names
    assert "12_mixed_shift.mp4" in names
    assert len(catalog) == 12
    assert all(item["offline"] is True for item in catalog)


def test_assistant_explains_named_incident():
    incidents = [
        Incident(
            incident_id="HG-0001",
            video_id="v1",
            behaviour="drop",
            risk_score=82,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.88,
            start_time=4.2,
            end_time=4.8,
            primary_object_track="carton_1",
            actor_track=None,
            equipment_track=None,
            zone="staging",
            evidence={},
            explanation="A carton moved downward rapidly.",
            recommendation="Inspect the product for visible damage.",
            status=IncidentStatus.NEW,
            loading_bay="Bay-A",
        )
    ]
    reply = AssistantService(load_config(), lambda: incidents).query("Why was incident HG-0001 high risk?")
    assert reply.blocked is False
    assert reply.intent == "explain"
    assert "HG-0001" in reply.citations
    assert "82" in reply.answer
    assert "drop" in reply.answer.lower()
