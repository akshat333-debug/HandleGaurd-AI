from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.api.schemas import (
    AssistantOut,
    AssistantQuery,
    IncidentOut,
    IncidentPatch,
    VideoCreate,
    VideoOut,
    ZoneIn,
    ZoneOut,
)
from handleguard.assistant.service import AssistantService
from handleguard.config.loader import load_config
from handleguard.db.models import IncidentRow, VideoRow, ZoneRow
from handleguard.db.repositories import (
    analytics_summary,
    delete_zone,
    get_incident,
    get_video,
    list_incidents,
    list_videos,
    list_zones,
    patch_incident,
    save_incident,
    save_video,
    upsert_zone,
)
from handleguard.db.session import get_session, init_db
from handleguard.demo import DEMO_TIMELINE, demo_timestamps
from handleguard.incidents.reports import incident_report_json, incident_report_markdown
from handleguard.metrics.ablation import run_ablation
from handleguard.metrics.behaviour import EventInterval
from handleguard.metrics.error_cards import error_card
from handleguard.metrics.feedback import ReviewLabel, feedback_metrics
from handleguard.metrics.impact import estimated_avoided_loss
from handleguard.video.clip_writer import write_clip_sidecar
from handleguard.incidents.clips import plan_clip
from handleguard.video.overlay import OverlayBox, plan_overlay
from handleguard.logging import log_event
from handleguard.observability import OBS, snapshot
from handleguard.pipeline import HandleGuardPipeline
from handleguard.pipeline_errors import HandleGuardError
from handleguard.security.uploads import UploadRejected, validate_upload
from handleguard.types import Incident, IncidentStatus, RiskLevel

CONFIG = load_config()
ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "data" / "raw"
CLIP_DIR = ROOT / "data" / "clips"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    CLIP_DIR.mkdir(parents=True, exist_ok=True)
    yield


APP = FastAPI(title="HandleGuard AI", version="0.1.0", lifespan=lifespan)
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_session() -> Session:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@APP.exception_handler(UploadRejected)
def _upload_rejected(_request: Request, exc: UploadRejected) -> JSONResponse:
    OBS.record_error()
    log_event(level="ERROR", module="api", event="upload_rejected", error=str(exc))
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@APP.exception_handler(HandleGuardError)
def _pipeline_error(_request: Request, exc: HandleGuardError) -> JSONResponse:
    OBS.record_error()
    log_event(level="ERROR", module="api", event="pipeline_error", error=str(exc))
    return JSONResponse(status_code=400, content={"detail": str(exc)})


def _incident_out(row: IncidentRow) -> IncidentOut:
    try:
        evidence = json.loads(row.evidence_json or "{}")
    except json.JSONDecodeError:
        evidence = {}
    return IncidentOut(
        id=row.id,
        video_id=row.video_id,
        behaviour=row.behaviour,
        risk_score=row.risk_score,
        risk_level=row.risk_level,
        confidence=row.confidence,
        start_time=row.start_time,
        end_time=row.end_time,
        zone=row.zone,
        evidence=evidence,
        explanation=row.explanation,
        recommendation=row.recommendation,
        review_status=row.review_status,
        camera_id=row.camera_id,
        loading_bay=row.loading_bay,
        primary_object_track=row.primary_object_track,
        actor_track=row.actor_track,
        supervisor_note=row.supervisor_note,
        clip_path=row.clip_path,
        created_at=row.created_at,
    )


def _video_out(row: VideoRow) -> VideoOut:
    return VideoOut(
        id=row.id,
        filename=row.filename,
        source_type=row.source_type,
        duration=row.duration,
        fps=row.fps,
        width=row.width,
        height=row.height,
        camera_id=row.camera_id,
        loading_bay=row.loading_bay,
        status=row.status,
        created_at=row.created_at,
    )


def _row_to_incident(row: IncidentRow) -> Incident:
    try:
        evidence = json.loads(row.evidence_json or "{}")
    except json.JSONDecodeError:
        evidence = {}
    return Incident(
        incident_id=row.id,
        video_id=row.video_id,
        behaviour=row.behaviour,
        risk_score=row.risk_score,
        risk_level=RiskLevel(row.risk_level),
        confidence=row.confidence,
        start_time=row.start_time,
        end_time=row.end_time,
        primary_object_track=row.primary_object_track,
        actor_track=row.actor_track,
        equipment_track=None,
        zone=row.zone,
        evidence=evidence,
        explanation=row.explanation,
        recommendation=row.recommendation,
        status=IncidentStatus(row.review_status),
        camera_id=row.camera_id,
        loading_bay=row.loading_bay,
        clip_path=row.clip_path,
        thumbnail_path=row.thumbnail_path,
        supervisor_note=row.supervisor_note,
    )


@APP.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "handleguard-ai"}


@APP.get("/api/observability")
def observability() -> dict[str, object]:
    return snapshot(OBS)


@APP.post("/api/videos", response_model=VideoOut)
def create_video(payload: VideoCreate, session: Session = Depends(db_session)) -> VideoOut:
    video_id = f"vid-{uuid4().hex[:8]}"
    row = save_video(
        session,
        video_id=video_id,
        filename=payload.filename,
        source_type=payload.source_type,
        camera_id=payload.camera_id,
        loading_bay=payload.loading_bay,
        status="uploaded",
    )
    return _video_out(row)


@APP.post("/api/videos/upload", response_model=VideoOut)
async def upload_video(
    file: UploadFile = File(...),
    loading_bay: str = Query("Bay-A"),
    camera_id: str = Query("cam-01"),
    session: Session = Depends(db_session),
) -> VideoOut:
    raw = await file.read()
    max_mb = float(CONFIG.video.get("video", {}).get("max_upload_mb", 200))
    allowed = set(CONFIG.video.get("video", {}).get("allowed_extensions", [".mp4", ".avi", ".mov", ".mkv"]))
    checked = validate_upload(file.filename or "upload.mp4", len(raw), max_mb=max_mb, allowed=allowed)
    video_id = f"vid-{uuid4().hex[:8]}"
    dest = UPLOAD_DIR / f"{video_id}{Path(checked.safe_name).suffix.lower()}"
    dest.write_bytes(raw)
    OBS.queued_videos += 1
    log_event(level="INFO", module="api", event="video_uploaded", video_id=video_id)
    row = save_video(
        session,
        video_id=video_id,
        filename=checked.safe_name,
        source_type="upload",
        camera_id=camera_id,
        loading_bay=loading_bay,
        status="uploaded",
    )
    return _video_out(row)


@APP.get("/api/videos", response_model=list[VideoOut])
def videos(session: Session = Depends(db_session)) -> list[VideoOut]:
    return [_video_out(row) for row in list_videos(session)]


@APP.get("/api/videos/{video_id}", response_model=VideoOut)
def video_detail(video_id: str, session: Session = Depends(db_session)) -> VideoOut:
    row = get_video(session, video_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return _video_out(row)


@APP.post("/api/videos/{video_id}/process", response_model=list[IncidentOut])
def process_video(video_id: str, session: Session = Depends(db_session)) -> list[IncidentOut]:
    row = get_video(session, video_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Video not found")
    pipeline = HandleGuardPipeline.from_stub(DEMO_TIMELINE, config=CONFIG, video_id=video_id)
    pipeline.camera_id = row.camera_id
    pipeline.loading_bay = row.loading_bay
    OBS.queued_videos = max(0, OBS.queued_videos - 1)
    result = pipeline.process_timeline(demo_timestamps())
    OBS.record_frame(latency_ms=1.0 * max(result.frames_processed, 1))
    saved = []
    for incident in result.incidents:
        plan = plan_clip(
            incident.incident_id,
            incident.start_time,
            incident.end_time,
            pipeline.engine.video_duration,
        )
        write_clip_sidecar(plan, CLIP_DIR)
        saved.append(save_incident(session, incident))
        OBS.record_incident()
    row.status = "processed"
    session.commit()
    log_event(
        level="INFO",
        module="api",
        event="video_processed",
        video_id=video_id,
        latency_ms=float(result.frames_processed),
    )
    return [_incident_out(item) for item in saved]


@APP.get("/api/incidents", response_model=list[IncidentOut])
def incidents(
    behaviour: str | None = None,
    risk_level: str | None = None,
    status: str | None = None,
    video_id: str | None = None,
    session: Session = Depends(db_session),
) -> list[IncidentOut]:
    rows = list_incidents(
        session,
        behaviour=behaviour,
        risk_level=risk_level,
        status=status,
        video_id=video_id,
    )
    return [_incident_out(row) for row in rows]


@APP.get("/api/incidents/{incident_id}", response_model=IncidentOut)
def incident_detail(incident_id: str, session: Session = Depends(db_session)) -> IncidentOut:
    row = get_incident(session, incident_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_out(row)


@APP.patch("/api/incidents/{incident_id}", response_model=IncidentOut)
def incident_patch(
    incident_id: str,
    payload: IncidentPatch,
    session: Session = Depends(db_session),
) -> IncidentOut:
    row = patch_incident(
        session,
        incident_id,
        review_status=payload.review_status,
        supervisor_note=payload.supervisor_note,
        risk_level=payload.risk_level,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_out(row)


@APP.get("/api/incidents/{incident_id}/report")
def incident_report(
    incident_id: str,
    fmt: str = Query("json"),
    session: Session = Depends(db_session),
) -> dict[str, Any] | str:
    row = get_incident(session, incident_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = _row_to_incident(row)
    if fmt == "markdown":
        return {"incident_id": incident.incident_id, "markdown": incident_report_markdown(incident)}
    return incident_report_json(incident)


@APP.get("/api/incidents/{incident_id}/clip")
def incident_clip(incident_id: str, session: Session = Depends(db_session)) -> dict[str, Any]:
    row = get_incident(session, incident_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    overlay = plan_overlay(
        timestamp=row.start_time,
        boxes=[
            OverlayBox(
                row.primary_object_track or "object",
                "product",
                (0.0, 0.0, 0.0, 0.0),
                row.behaviour,
            )
        ],
        risk_score=row.risk_score,
        behaviour=row.behaviour,
    )
    return {
        "incident_id": row.id,
        "clip_path": row.clip_path,
        "start_time": max(0.0, row.start_time - 3),
        "end_time": row.end_time + 4,
        "overlay": {"caption": overlay.caption, "timestamp": overlay.timestamp},
        "message": "Clip metadata ready. Bind a media encoder in production.",
    }


@APP.get("/api/metrics/impact")
def metrics_impact(session: Session = Depends(db_session)) -> dict[str, Any]:
    summary = analytics_summary(session)
    high = summary["by_level"].get("High", 0) + summary["by_level"].get("Critical", 0)
    loss = estimated_avoided_loss(n_preventable=high, p_damage=0.2, cost=50.0)
    return {
        "preventable_high_risk_events": high,
        "estimated_avoided_loss": loss.value,
        "assumption": loss.assumption_label,
    }


@APP.get("/api/metrics/errors")
def metrics_errors(session: Session = Depends(db_session)) -> dict[str, Any]:
    rows = list_incidents(session, status="FALSE_POSITIVE")
    cards = [
        error_card(
            incident_id=row.id,
            behaviour=row.behaviour,
            trigger=row.explanation,
            rejection=row.supervisor_note or "marked false positive",
            signal="review",
        )
        for row in rows
    ]
    return {
        "count": len(cards),
        "cards": [
            {
                "incident_id": card.incident_id,
                "behaviour": card.behaviour,
                "category": card.category,
                "why_system_triggered": card.why_system_triggered,
                "why_human_rejected": card.why_human_rejected,
                "fix": card.fix,
            }
            for card in cards
        ],
    }


@APP.get("/api/metrics/feedback")
def metrics_feedback(session: Session = Depends(db_session)) -> dict[str, Any]:
    rows = list_incidents(session)
    report = feedback_metrics(
        [ReviewLabel(row.id, row.behaviour, row.review_status) for row in rows]
    )
    return {
        "reviewed": report.reviewed,
        "confirmed": report.confirmed,
        "false_positives": report.false_positives,
        "precision": report.precision,
        "by_behaviour": {
            name: {
                "confirmed": item.confirmed,
                "false_positives": item.false_positives,
                "reviewed": item.reviewed,
            }
            for name, item in report.by_behaviour.items()
        },
    }


@APP.get("/api/metrics/ablation")
def metrics_ablation() -> dict[str, Any]:
    truths = [
        EventInterval("drop", 0.5, 2.0),
        EventInterval("throw", 2.1, 3.1),
        EventInterval("drag", 3.5, 5.5),
    ]
    report = run_ablation(DEMO_TIMELINE, demo_timestamps(), truths, config=CONFIG)
    return {
        "variants": {
            name: {
                "precision": variant.macro.precision,
                "recall": variant.macro.recall,
                "f1": variant.macro.f1,
                "tp": variant.macro.tp,
                "fp": variant.macro.fp,
                "fn": variant.macro.fn,
            }
            for name, variant in report.variants.items()
        }
    }


@APP.get("/api/analytics/summary")
def analytics(session: Session = Depends(db_session)) -> dict[str, Any]:
    return analytics_summary(session)


@APP.get("/api/analytics/behaviours")
def analytics_behaviours(session: Session = Depends(db_session)) -> dict[str, int]:
    return analytics_summary(session)["by_behaviour"]


@APP.get("/api/analytics/risk")
def analytics_risk(session: Session = Depends(db_session)) -> dict[str, int]:
    return analytics_summary(session)["by_level"]


@APP.get("/api/analytics/bays")
def analytics_bays(session: Session = Depends(db_session)) -> dict[str, int]:
    return analytics_summary(session)["by_bay"]


@APP.post("/api/assistant/query", response_model=AssistantOut)
def assistant_query(payload: AssistantQuery, session: Session = Depends(db_session)) -> AssistantOut:
    service = AssistantService(
        CONFIG,
        lambda: [_row_to_incident(row) for row in list_incidents(session)],
    )
    reply = service.query(payload.question)
    return AssistantOut(
        answer=reply.answer,
        citations=reply.citations,
        blocked=reply.blocked,
        intent=reply.intent,
    )


@APP.get("/api/config/behaviours")
def get_behaviours() -> dict[str, Any]:
    return CONFIG.behaviours


@APP.patch("/api/config/behaviours")
def patch_behaviours(payload: dict[str, Any]) -> dict[str, Any]:
    for key, value in payload.items():
        if key in CONFIG.behaviours and isinstance(CONFIG.behaviours[key], dict) and isinstance(value, dict):
            CONFIG.behaviours[key].update(value)
    return CONFIG.behaviours


@APP.get("/api/zones", response_model=list[ZoneOut])
def zones(session: Session = Depends(db_session)) -> list[ZoneOut]:
    rows = list_zones(session)
    if rows:
        return [
            ZoneOut(
                id=row.id,
                name=row.name,
                camera_id=row.camera_id,
                polygon=json.loads(row.polygon_json),
                zone_type=row.zone_type,
            )
            for row in rows
        ]
    fallback = []
    for idx, item in enumerate(CONFIG.zones.get("zones", []), start=1):
        fallback.append(
            ZoneOut(
                id=idx,
                name=item["name"],
                camera_id=item.get("camera_id", "cam-01"),
                polygon=item["polygon"],
                zone_type=item["type"],
            )
        )
    return fallback


@APP.post("/api/zones", response_model=ZoneOut)
def create_zone(payload: ZoneIn, session: Session = Depends(db_session)) -> ZoneOut:
    row = upsert_zone(
        session,
        name=payload.name,
        camera_id=payload.camera_id,
        polygon_json=json.dumps(payload.polygon),
        zone_type=payload.zone_type,
    )
    return ZoneOut(
        id=row.id,
        name=row.name,
        camera_id=row.camera_id,
        polygon=json.loads(row.polygon_json),
        zone_type=row.zone_type,
    )


@APP.patch("/api/zones/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: int, payload: ZoneIn, session: Session = Depends(db_session)) -> ZoneOut:
    row = upsert_zone(
        session,
        name=payload.name,
        camera_id=payload.camera_id,
        polygon_json=json.dumps(payload.polygon),
        zone_type=payload.zone_type,
        zone_id=zone_id,
    )
    return ZoneOut(
        id=row.id,
        name=row.name,
        camera_id=row.camera_id,
        polygon=json.loads(row.polygon_json),
        zone_type=row.zone_type,
    )


@APP.delete("/api/zones/{zone_id}")
def remove_zone(zone_id: int, session: Session = Depends(db_session)) -> dict[str, bool]:
    if not delete_zone(session, zone_id):
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"ok": True}


app = APP
