from __future__ import annotations

from typing import Any

IDENTITY_KEYS = {
    "worker_name",
    "employee_id",
    "employee_name",
    "person_name",
    "face_id",
    "face",
    "identity",
    "worker_id",
}


def redact_identity(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key.lower() not in IDENTITY_KEYS}
