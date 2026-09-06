from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


BBox = tuple[float, float, float, float]
Point = tuple[float, float]
Polygon = list[Point]


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IncidentStatus(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    UNDER_REVIEW = "UNDER_REVIEW"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class ZoneType(str, Enum):
    ALLOWED = "allowed"
    RESTRICTED_PRODUCT = "restricted_product"
    RESTRICTED = "restricted"
    UNSAFE_SURFACE = "unsafe_surface"


PRODUCT_CLASSES = frozenset(
    {"carton", "box", "product", "electronics", "mattress", "glass", "pallet"}
)
PERSON_CLASSES = frozenset({"person", "human"})
EQUIPMENT_CLASSES = frozenset({"forklift", "trolley", "pallet_jack", "pallet-jack"})
PALLET_CLASSES = frozenset({"pallet"})


def is_product(class_name: str) -> bool:
    name = class_name.lower()
    return name in PRODUCT_CLASSES or name.startswith("product")


def is_person(class_name: str) -> bool:
    return class_name.lower() in PERSON_CLASSES


def is_equipment(class_name: str) -> bool:
    return class_name.lower() in EQUIPMENT_CLASSES


def is_pallet(class_name: str) -> bool:
    return class_name.lower() in PALLET_CLASSES


@dataclass(slots=True)
class Detection:
    class_name: str
    bbox: BBox
    confidence: float


@dataclass(slots=True)
class HistoryEntry:
    timestamp: float
    bbox: BBox
    center: Point
    width: float
    height: float
    confidence: float
    zone: str | None = None


@dataclass
class TrackState:
    track_id: str
    class_name: str
    bbox: BBox
    confidence: float
    first_seen: float
    last_seen: float
    history: list[HistoryEntry] = field(default_factory=list)
    velocity: Point = (0.0, 0.0)
    acceleration: Point = (0.0, 0.0)
    zone: str | None = None
    related_tracks: list[str] = field(default_factory=list)

    @property
    def age(self) -> float:
        return self.last_seen - self.first_seen


@dataclass(slots=True)
class Zone:
    name: str
    zone_type: ZoneType
    polygon: Polygon
    camera_id: str = "cam-01"


@dataclass(slots=True)
class BehaviourEvidence:
    behaviour: str
    start_time: float
    end_time: float
    entities: list[str]
    raw_score: float
    evidence: dict[str, Any]


@dataclass
class Incident:
    incident_id: str
    video_id: str
    behaviour: str
    risk_score: float
    risk_level: RiskLevel
    confidence: float
    start_time: float
    end_time: float
    primary_object_track: str | None
    actor_track: str | None
    equipment_track: str | None
    zone: str | None
    evidence: dict[str, Any]
    explanation: str
    recommendation: str
    status: IncidentStatus = IncidentStatus.NEW
    camera_id: str = "cam-01"
    loading_bay: str | None = None
    clip_path: str | None = None
    thumbnail_path: str | None = None
    review_label: str | None = None
    supervisor_note: str | None = None
