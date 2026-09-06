from __future__ import annotations

from typing import Any, Iterable

from handleguard.features.geometry import bbox_center, point_in_polygon
from handleguard.types import BBox, Zone, ZoneType


def zone_from_config(item: dict[str, Any]) -> Zone:
    polygon = [tuple(pair) for pair in item["polygon"]]
    return Zone(
        name=str(item["name"]),
        zone_type=ZoneType(item["type"]),
        polygon=polygon,
        camera_id=str(item.get("camera_id", "cam-01")),
    )


def load_zones(raw: dict[str, Any] | list[dict[str, Any]]) -> list[Zone]:
    items = raw["zones"] if isinstance(raw, dict) else raw
    return [zone_from_config(item) for item in items]


_ZONE_PRIORITY = {
    ZoneType.UNSAFE_SURFACE: 0,
    ZoneType.RESTRICTED: 1,
    ZoneType.RESTRICTED_PRODUCT: 2,
    ZoneType.ALLOWED: 3,
}


def resolve_zone(bbox: BBox, zones: Iterable[Zone]) -> Zone | None:
    point = bbox_center(bbox)
    matches = [zone for zone in zones if point_in_polygon(point, zone.polygon)]
    if not matches:
        return None
    matches.sort(key=lambda zone: _ZONE_PRIORITY.get(zone.zone_type, 9))
    return matches[0]
