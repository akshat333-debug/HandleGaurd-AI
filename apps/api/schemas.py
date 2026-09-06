from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VideoOut(BaseModel):
    id: str
    filename: str
    source_type: str
    duration: float
    fps: float
    width: int
    height: int
    camera_id: str
    loading_bay: str | None
    status: str
    created_at: datetime


class VideoCreate(BaseModel):
    filename: str
    loading_bay: str | None = "Bay-A"
    camera_id: str = "cam-01"
    source_type: str = "upload"


class IncidentOut(BaseModel):
    id: str
    video_id: str
    behaviour: str
    risk_score: float
    risk_level: str
    confidence: float
    start_time: float
    end_time: float
    zone: str | None
    evidence: dict[str, Any] = Field(default_factory=dict)
    explanation: str
    recommendation: str
    review_status: str
    camera_id: str
    loading_bay: str | None
    primary_object_track: str | None
    actor_track: str | None
    supervisor_note: str | None
    clip_path: str | None = None
    created_at: datetime


class IncidentPatch(BaseModel):
    review_status: str | None = None
    supervisor_note: str | None = None
    risk_level: str | None = None


class AssistantQuery(BaseModel):
    question: str


class AssistantOut(BaseModel):
    answer: str
    citations: list[str]
    blocked: bool
    intent: str


class ZoneIn(BaseModel):
    name: str
    camera_id: str = "cam-01"
    polygon: list[list[float]]
    zone_type: str


class ZoneOut(BaseModel):
    id: int
    name: str
    camera_id: str
    polygon: list[list[float]]
    zone_type: str
