from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from handleguard.config.loader import AppConfig
from handleguard.events.graph import EventGraph
from handleguard.types import BehaviourEvidence, TrackState, Zone


@dataclass
class BehaviourContext:
    timestamp: float
    tracks: list[TrackState]
    graph: EventGraph
    zones: list[Zone]
    config: AppConfig
    extras: dict[str, Any] = field(default_factory=dict)


class BehaviourDetector(Protocol):
    name: str

    def update(self, context: BehaviourContext) -> list[BehaviourEvidence]:
        ...
