from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class VideoRow(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(512))
    source_type: Mapped[str] = mapped_column(String(32), default="upload")
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    fps: Mapped[float] = mapped_column(Float, default=8.0)
    width: Mapped[int] = mapped_column(Integer, default=1280)
    height: Mapped[int] = mapped_column(Integer, default=720)
    camera_id: Mapped[str] = mapped_column(String(64), default="cam-01")
    loading_bay: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())

    incidents: Mapped[list["IncidentRow"]] = relationship(back_populates="video")


class IncidentRow(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    behaviour: Mapped[str] = mapped_column(String(64), index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    zone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    clip_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    explanation: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(Text, default="")
    review_status: Mapped[str] = mapped_column(String(32), default="NEW")
    camera_id: Mapped[str] = mapped_column(String(64), default="cam-01")
    loading_bay: Mapped[str | None] = mapped_column(String(64), nullable=True)
    primary_object_track: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actor_track: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supervisor_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())

    video: Mapped[VideoRow] = relationship(back_populates="incidents")
    entities: Mapped[list["IncidentEntityRow"]] = relationship(back_populates="incident")
    reviews: Mapped[list["ReviewRow"]] = relationship(back_populates="incident")


class IncidentEntityRow(Base):
    __tablename__ = "incident_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"))
    track_id: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(32), default="product")
    role: Mapped[str] = mapped_column(String(32), default="primary")

    incident: Mapped[IncidentRow] = relationship(back_populates="entities")


class ReviewRow(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"))
    label: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(Text, default="")
    reviewer_role: Mapped[str] = mapped_column(String(32), default="supervisor")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    incident: Mapped[IncidentRow] = relationship(back_populates="reviews")


class ZoneRow(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(String(64), default="cam-01")
    name: Mapped[str] = mapped_column(String(64))
    polygon_json: Mapped[str] = mapped_column(Text)
    zone_type: Mapped[str] = mapped_column(String(32))


class SopRuleRow(Base):
    __tablename__ = "sop_rules"

    behaviour: Mapped[str] = mapped_column(String(64), primary_key=True)
    rule_text: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)


class MetricsRunRow(Base):
    __tablename__ = "metrics_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_version: Mapped[str] = mapped_column(String(64))
    dataset_version: Mapped[str] = mapped_column(String(64))
    metrics_json: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
