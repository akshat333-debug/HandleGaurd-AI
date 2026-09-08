from __future__ import annotations

from dataclasses import dataclass

from handleguard.config.loader import AppConfig, load_config
from handleguard.metrics.behaviour import EventInterval, EventReport, evaluate_events
from handleguard.metrics.reports import incidents_to_events
from handleguard.pipeline import HandleGuardPipeline
from handleguard.types import Detection


@dataclass
class AblationReport:
    variants: dict[str, EventReport]


def run_ablation(
    timeline: list[tuple[float, list[Detection]]],
    timestamps: list[float],
    truths: list[EventInterval],
    *,
    config: AppConfig | None = None,
) -> AblationReport:
    cfg = config or load_config()
    variants: dict[str, EventReport] = {}
    settings = {
        "full": {"use_tracker": True, "use_event_graph": True},
        "no_tracking": {"use_tracker": False, "use_event_graph": True},
        "no_event_graph": {"use_tracker": True, "use_event_graph": False},
    }
    for name, flags in settings.items():
        pipeline = HandleGuardPipeline.from_stub(
            timeline,
            config=cfg,
            video_id=f"ablation-{name}",
            use_tracker=flags["use_tracker"],
            use_event_graph=flags["use_event_graph"],
        )
        result = pipeline.process_timeline(timestamps)
        variants[name] = evaluate_events(incidents_to_events(result.incidents), truths)
    return AblationReport(variants=variants)
