from __future__ import annotations

from datetime import datetime, timedelta, timezone

from handleguard.demo_pack import DEMO_ANNOTATIONS, demo_annotation_pack
from handleguard.metrics.kpis import mean_response_seconds
from handleguard.video.annotations import parse_annotation


def test_mean_response_seconds_from_pairs():
    created = datetime(2026, 9, 8, 10, 0, tzinfo=timezone.utc)
    reviewed = created + timedelta(seconds=45)
    later = created + timedelta(seconds=15)
    mean = mean_response_seconds([(created, reviewed), (created, later)])
    assert mean == 30.0


def test_mean_response_seconds_empty():
    assert mean_response_seconds([]) == 0.0


def test_demo_annotation_pack_has_ten_behaviours():
    pack = demo_annotation_pack()
    assert pack["video_id"] == "demo"
    record = parse_annotation(pack)
    behaviours = {event.behaviour for event in record.events}
    assert len(behaviours) >= 8
    assert "drop" in behaviours
    assert record.events[0].start_s < record.events[0].end_s
    assert DEMO_ANNOTATIONS["video_id"] == "demo"
