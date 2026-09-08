from __future__ import annotations

from dataclasses import dataclass, field

from handleguard.metrics.detection import ClassificationMetrics, prf1


@dataclass(frozen=True, slots=True)
class EventInterval:
    behaviour: str
    start_time: float
    end_time: float


@dataclass
class EventReport:
    by_behaviour: dict[str, ClassificationMetrics]
    macro: ClassificationMetrics
    matched: list[tuple[EventInterval, EventInterval]] = field(default_factory=list)


def temporal_iou(a: EventInterval, b: EventInterval) -> float:
    if a.behaviour != b.behaviour:
        return 0.0
    start = max(a.start_time, b.start_time)
    end = min(a.end_time, b.end_time)
    inter = max(0.0, end - start)
    union = max(a.end_time, b.end_time) - min(a.start_time, b.start_time)
    if union <= 0:
        return 1.0 if inter == 0 and a.start_time == b.start_time else 0.0
    return inter / union


def evaluate_events(
    predictions: list[EventInterval],
    truths: list[EventInterval],
    iou_threshold: float = 0.3,
) -> EventReport:
    behaviours = sorted({e.behaviour for e in predictions} | {e.behaviour for e in truths})
    used_truths: set[int] = set()
    matched: list[tuple[EventInterval, EventInterval]] = []
    tp_map: dict[str, int] = {b: 0 for b in behaviours}
    fp_map: dict[str, int] = {b: 0 for b in behaviours}
    fn_map: dict[str, int] = {b: 0 for b in behaviours}

    for pred in predictions:
        best_idx = None
        best_iou = iou_threshold
        for idx, truth in enumerate(truths):
            if idx in used_truths:
                continue
            score = temporal_iou(pred, truth)
            if score >= best_iou:
                best_iou = score
                best_idx = idx
        if best_idx is None:
            fp_map[pred.behaviour] = fp_map.get(pred.behaviour, 0) + 1
        else:
            used_truths.add(best_idx)
            tp_map[pred.behaviour] = tp_map.get(pred.behaviour, 0) + 1
            matched.append((pred, truths[best_idx]))

    for idx, truth in enumerate(truths):
        if idx not in used_truths:
            fn_map[truth.behaviour] = fn_map.get(truth.behaviour, 0) + 1

    by_behaviour = {
        name: prf1(tp_map.get(name, 0), fp_map.get(name, 0), fn_map.get(name, 0))
        for name in behaviours
    }
    totals = prf1(sum(tp_map.values()), sum(fp_map.values()), sum(fn_map.values()))
    if by_behaviour:
        n = len(by_behaviour)
        macro = ClassificationMetrics(
            precision=round(sum(m.precision for m in by_behaviour.values()) / n, 6),
            recall=round(sum(m.recall for m in by_behaviour.values()) / n, 6),
            f1=round(sum(m.f1 for m in by_behaviour.values()) / n, 6),
            tp=totals.tp,
            fp=totals.fp,
            fn=totals.fn,
        )
    else:
        macro = totals
    return EventReport(by_behaviour=by_behaviour, macro=macro, matched=matched)
