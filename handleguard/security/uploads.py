from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


class UploadRejected(ValueError):
    """Raised when an upload fails type, size, or name checks."""


@dataclass(frozen=True, slots=True)
class UploadResult:
    ok: bool
    safe_name: str
    size_bytes: int


def validate_upload(
    filename: str,
    size_bytes: int,
    max_mb: float = 200,
    allowed: set[str] | None = None,
) -> UploadResult:
    allowed_ext = allowed or ALLOWED_EXTENSIONS
    raw = Path(filename.replace("\\", "/")).name
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in {".", "-", "_"}).lstrip(".")
    if not safe:
        safe = "upload.bin"
    suffix = Path(safe).suffix.lower()
    if suffix not in allowed_ext:
        raise UploadRejected(f"Unsupported video type: {suffix or 'unknown'}")
    max_bytes = int(max_mb * 1024 * 1024)
    if size_bytes > max_bytes:
        raise UploadRejected(f"File too large: {size_bytes} exceeds {max_bytes} bytes")
    if size_bytes < 0:
        raise UploadRejected("Invalid file size")
    return UploadResult(ok=True, safe_name=safe, size_bytes=size_bytes)
