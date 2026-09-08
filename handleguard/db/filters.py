from __future__ import annotations

from datetime import datetime


def incident_matches(
    *,
    loading_bay: str | None,
    created_at: datetime | None,
    bay: str | None,
    start: datetime | None,
    end: datetime | None,
    camera_id: str | None = None,
    row_camera_id: str | None = None,
) -> bool:
    if bay and (loading_bay or "") != bay:
        return False
    if camera_id and (row_camera_id or "") != camera_id:
        return False
    if start and (created_at is None or created_at < start):
        return False
    if end and (created_at is None or created_at >= end):
        return False
    return True
