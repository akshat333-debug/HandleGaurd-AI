from __future__ import annotations

from typing import Iterable

from handleguard.metrics.behaviour import EventInterval
from handleguard.types import Incident


def incidents_to_events(incidents: Iterable[Incident]) -> list[EventInterval]:
    return [
        EventInterval(behaviour=item.behaviour, start_time=item.start_time, end_time=item.end_time)
        for item in incidents
    ]
