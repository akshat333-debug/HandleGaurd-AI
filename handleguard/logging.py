from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def log_event(
    *,
    level: str,
    module: str,
    event: str,
    video_id: str | None = None,
    latency_ms: float | None = None,
    error: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "module": module,
        "event": event,
        "video_id": video_id,
        "latency_ms": latency_ms,
        "error": error or "",
    }
    payload.update(extra)
    print(json.dumps(payload, default=str), flush=True)
    return payload
