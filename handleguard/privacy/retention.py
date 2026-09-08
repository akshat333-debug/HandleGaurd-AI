from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable


def expired_paths(
    files: Iterable[tuple[str, datetime]],
    *,
    now: datetime,
    retain_days: int,
) -> list[str]:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    cutoff = now - timedelta(days=retain_days)
    expired: list[str] = []
    for path, stamped in files:
        stamp = stamped if stamped.tzinfo else stamped.replace(tzinfo=timezone.utc)
        if stamp < cutoff:
            expired.append(path)
    return expired
