from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from handleguard.db.filters import incident_matches
from handleguard.db.models import IncidentRow, ReviewRow, VideoRow, ZoneRow
from handleguard.types import Incident


def save_video(
    session: Session,
    *,
    video_id: str,
    filename: str,
    source_type: str = "upload",
    duration: float = 0.0,
    fps: float = 8.0,
    width: int = 1280,
    height: int = 720,
    camera_id: str = "cam-01",
    loading_bay: str | None = "Bay-A",
    status: str = "uploaded",
) -> VideoRow:
    row = session.get(VideoRow, video_id)
    if row is None:
        row = VideoRow(id=video_id)
        session.add(row)
    row.filename = filename
    row.source_type = source_type
    row.duration = duration
    row.fps = fps
    row.width = width
    row.height = height
    row.camera_id = camera_id
    row.loading_bay = loading_bay
    row.status = status
    session.commit()
    session.refresh(row)
    return row


def save_incident(session: Session, incident: Incident) -> IncidentRow:
    row = IncidentRow(
        id=incident.incident_id,
        video_id=incident.video_id,
        behaviour=incident.behaviour,
        risk_score=incident.risk_score,
        risk_level=incident.risk_level.value,
        confidence=incident.confidence,
        start_time=incident.start_time,
        end_time=incident.end_time,
        zone=incident.zone,
        evidence_json=json.dumps(incident.evidence),
        clip_path=incident.clip_path,
        thumbnail_path=incident.thumbnail_path,
        explanation=incident.explanation,
        recommendation=incident.recommendation,
        review_status=incident.status.value,
        camera_id=incident.camera_id,
        loading_bay=incident.loading_bay,
        primary_object_track=incident.primary_object_track,
        actor_track=incident.actor_track,
        supervisor_note=incident.supervisor_note,
        created_at=datetime.now(timezone.utc),
    )
    merged = session.merge(row)
    session.commit()
    session.refresh(merged)
    return merged


def list_incidents(
    session: Session,
    *,
    behaviour: str | None = None,
    risk_level: str | None = None,
    status: str | None = None,
    video_id: str | None = None,
    loading_bay: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[IncidentRow]:
    stmt: Select[tuple[IncidentRow]] = select(IncidentRow).order_by(IncidentRow.created_at.desc())
    if behaviour:
        stmt = stmt.where(IncidentRow.behaviour == behaviour)
    if risk_level:
        stmt = stmt.where(IncidentRow.risk_level == risk_level)
    if status:
        stmt = stmt.where(IncidentRow.review_status == status)
    if video_id:
        stmt = stmt.where(IncidentRow.video_id == video_id)
    rows = list(session.scalars(stmt))
    if loading_bay or start or end:
        rows = [
            row
            for row in rows
            if incident_matches(
                loading_bay=row.loading_bay,
                created_at=row.created_at,
                bay=loading_bay,
                start=start,
                end=end,
            )
        ]
    return rows


def get_incident(session: Session, incident_id: str) -> IncidentRow | None:
    return session.get(IncidentRow, incident_id)


def patch_incident(
    session: Session,
    incident_id: str,
    *,
    review_status: str | None = None,
    supervisor_note: str | None = None,
    risk_level: str | None = None,
    reviewer_role: str = "supervisor",
) -> IncidentRow | None:
    row = session.get(IncidentRow, incident_id)
    if row is None:
        return None
    if review_status:
        row.review_status = review_status
        session.add(
            ReviewRow(
                incident_id=incident_id,
                label=review_status,
                comment=supervisor_note or "",
                reviewer_role=reviewer_role,
            )
        )
    if supervisor_note is not None:
        row.supervisor_note = supervisor_note
    if risk_level:
        row.risk_level = risk_level
    session.commit()
    session.refresh(row)
    return row


def analytics_summary(session: Session) -> dict[str, Any]:
    rows = list(session.scalars(select(IncidentRow)))
    by_level: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    by_behaviour: dict[str, int] = {}
    by_bay: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for row in rows:
        by_level[row.risk_level] = by_level.get(row.risk_level, 0) + 1
        by_behaviour[row.behaviour] = by_behaviour.get(row.behaviour, 0) + 1
        bay = row.loading_bay or "unknown"
        by_bay[bay] = by_bay.get(bay, 0) + 1
        by_status[row.review_status] = by_status.get(row.review_status, 0) + 1
    return {
        "total": len(rows),
        "by_level": by_level,
        "by_behaviour": by_behaviour,
        "by_bay": by_bay,
        "by_status": by_status,
    }


def list_videos(session: Session) -> list[VideoRow]:
    return list(session.scalars(select(VideoRow).order_by(VideoRow.created_at.desc())))


def get_video(session: Session, video_id: str) -> VideoRow | None:
    return session.get(VideoRow, video_id)


def list_zones(session: Session) -> list[ZoneRow]:
    return list(session.scalars(select(ZoneRow)))


def upsert_zone(
    session: Session,
    *,
    name: str,
    camera_id: str,
    polygon_json: str,
    zone_type: str,
    zone_id: int | None = None,
) -> ZoneRow:
    row = session.get(ZoneRow, zone_id) if zone_id else None
    if row is None:
        row = ZoneRow()
        session.add(row)
    row.name = name
    row.camera_id = camera_id
    row.polygon_json = polygon_json
    row.zone_type = zone_type
    session.commit()
    session.refresh(row)
    return row


def delete_zone(session: Session, zone_id: int) -> bool:
    row = session.get(ZoneRow, zone_id)
    if row is None:
        return False
    session.delete(row)
    session.commit()
    return True
