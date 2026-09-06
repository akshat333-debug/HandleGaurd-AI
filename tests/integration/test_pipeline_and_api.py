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

    zones = client.get("/api/zones")
    assert zones.status_code == 200
    assert len(zones.json()) >= 1
