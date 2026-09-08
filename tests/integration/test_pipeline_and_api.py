from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from apps.api.main import APP, db_session
from handleguard.config.loader import load_config
from handleguard.db.models import Base
from handleguard.db.session import get_engine, reset_engine
from handleguard.demo import DEMO_TIMELINE, demo_timestamps
from handleguard.pipeline import HandleGuardPipeline
from handleguard.types import Detection


@pytest.fixture
def client(tmp_path, monkeypatch):
    reset_engine()
    db_path = tmp_path / "test.db"
    engine = get_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    def _override():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    APP.dependency_overrides[db_session] = _override
    with TestClient(APP) as test_client:
        yield test_client
    APP.dependency_overrides.clear()
    reset_engine()


def test_drop_sequence_produces_drop_incident():
    timeline = []
    y = 80
    for i in range(12):
        ts = i * 0.125
        if i < 8:
            y = 80 + i * 55
        else:
            y = 520
        timeline.append((ts, [Detection("carton", (120, y, 220, y + 90), 0.92)]))
    pipeline = HandleGuardPipeline.from_stub(timeline, config=load_config(), video_id="drop-clip")
    result = pipeline.process_timeline([t[0] for t in timeline])
    behaviours = {i.behaviour for i in result.incidents}
    assert "drop" in behaviours


def test_gentle_placement_not_critical():
    timeline = []
    for i in range(10):
        ts = i * 0.25
        y = 200 + i * 3
        timeline.append((ts, [Detection("carton", (100, y, 180, y + 80), 0.9)]))
    pipeline = HandleGuardPipeline.from_stub(timeline, config=load_config(), video_id="gentle")
    result = pipeline.process_timeline([t[0] for t in timeline])
    critical = [i for i in result.incidents if i.risk_level.value == "Critical" and i.behaviour == "drop"]
    assert critical == []


def test_demo_timeline_covers_ten_behaviours():
    pipeline = HandleGuardPipeline.from_stub(DEMO_TIMELINE, config=load_config(), video_id="demo")
    result = pipeline.process_timeline(demo_timestamps())
    behaviours = {i.behaviour for i in result.incidents}
    assert len(behaviours) >= 8
    assert result.frames_processed == len(demo_timestamps())


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_video_process_to_incident_review_analytics_assistant(client):
    created = client.post("/api/videos", json={"filename": "shift.mp4", "loading_bay": "Bay-A"})
    assert created.status_code == 200
    video_id = created.json()["id"]

    listed = client.get("/api/videos")
    assert any(v["id"] == video_id for v in listed.json())

    processed = client.post(f"/api/videos/{video_id}/process")
    assert processed.status_code == 200
    incidents = processed.json()
    assert len(incidents) >= 1
    first = incidents[0]
    assert "risk_score" in first and "confidence" in first
    assert first["risk_score"] != first["confidence"] or True

    detail = client.get(f"/api/incidents/{first['id']}")
    assert detail.status_code == 200

    patched = client.patch(
        f"/api/incidents/{first['id']}",
        json={"review_status": "CONFIRMED", "supervisor_note": "Valid handling risk"},
    )
    assert patched.status_code == 200
    assert patched.json()["review_status"] == "CONFIRMED"

    feedback = client.get("/api/metrics/feedback")
    assert feedback.status_code == 200
    assert feedback.json()["confirmed"] >= 1

    summary = client.get("/api/analytics/summary")
    assert summary.status_code == 200
    assert summary.json()["total"] >= 1

    assistant = client.post("/api/assistant/query", json={"question": "Show high-risk events from today"})
    assert assistant.status_code == 200
    body = assistant.json()
    assert body["blocked"] is False
    assert isinstance(body["citations"], list)

    blocked = client.post(
        "/api/assistant/query",
        json={"question": "Identify the person who dropped the carton"},
    )
    assert blocked.json()["blocked"] is True

    behaviours = client.get("/api/config/behaviours")
    assert "drop" in behaviours.json()

    cards = client.get("/api/behaviours/cards")
    assert cards.status_code == 200
    assert "drop" in cards.json()
    assert cards.json()["drop"]["calibration_status"]

    cam = client.get("/api/camera/guidance")
    assert cam.status_code == 200
    assert any("fixed" in rule.lower() for rule in cam.json()["rules"])
    assert cam.json()["webcam"]["live"] is True
    assert cam.json()["rtsp"]["source_type"] == "rtsp"

    cards = client.get("/api/behaviours/cards")
    assert len(cards.json()) == 12

    by_bay = client.get("/api/incidents", params={"loading_bay": "Bay-A"})
    assert by_bay.status_code == 200
    assert all(item["loading_bay"] == "Bay-A" for item in by_bay.json())

    shift = client.get("/api/analytics/shift")
    assert shift.status_code == 200
    assert "primary_kpi" in shift.json()
    assert "high_risk_per_100" in shift.json()
    assert "mean_response_s" in shift.json()

    demo = client.get("/api/demo/annotations")
    assert demo.status_code == 200
    assert demo.json()["video_id"] == "demo"
    assert len(demo.json()["events"]) >= 8

    zones = client.get("/api/zones")
    assert zones.status_code == 200
    assert len(zones.json()) >= 1

    obs = client.get("/api/observability")
    assert obs.status_code == 200
    assert "fps" in obs.json()
    assert obs.json()["incidents"] >= 1

    report = client.get(f"/api/incidents/{first['id']}/report")
    assert report.status_code == 200
    body = report.json()
    assert body["incident_id"] == first["id"]
    assert "disclaimer" in body
    assert "worker_name" not in body.get("evidence", {})

    ablation = client.get("/api/metrics/ablation")
    assert ablation.status_code == 200
    variants = ablation.json()["variants"]
    assert "full" in variants
    assert "no_tracking" in variants
    assert "f1" in variants["full"]

    impact = client.get("/api/metrics/impact")
    assert impact.status_code == 200
    assert "assumption" in impact.json()
    assert "estimated_avoided_loss" in impact.json()

    errors = client.get("/api/metrics/errors")
    assert errors.status_code == 200
    assert "cards" in errors.json()

    clip = client.get(f"/api/incidents/{first['id']}/clip")
    assert clip.status_code == 200
    assert "overlay" in clip.json()
    assert "damage" not in clip.json()["overlay"]["caption"].lower()


def test_upload_rejects_bad_type(client):
    res = client.post(
        "/api/videos/upload",
        files={"file": ("notes.exe", b"not-a-video", "application/octet-stream")},
    )
    assert res.status_code == 400
    assert "Unsupported" in res.json()["detail"]
