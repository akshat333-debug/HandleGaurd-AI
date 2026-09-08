from __future__ import annotations

import json
from pathlib import Path

from handleguard.incidents.clips import ClipPlan


def write_clip_sidecar(plan: ClipPlan, directory: str | Path) -> Path:
    dest = Path(directory)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / Path(plan.filename).with_suffix(".json").name
    payload = {
        "incident_id": plan.incident_id,
        "start_time": plan.start_time,
        "end_time": plan.end_time,
        "filename": plan.filename,
        "encoder": "sidecar",
        "note": "OpenCV encoder not bound; sidecar records the 3s-pre / 4s-post clip window.",
    }
    path.write_text(json.dumps(payload, indent=2))
    return path
