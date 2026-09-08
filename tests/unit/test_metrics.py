from __future__ import annotations

from handleguard.metrics.detection import confusion_counts, prf1
from handleguard.metrics.behaviour import EventInterval, evaluate_events, temporal_iou
from handleguard.metrics.latency import LatencyStats, summarize_latencies


def test_prf1_known_counts():
    metrics = prf1(tp=8, fp=2, fn=2)
    assert metrics.precision == 0.8
    assert metrics.recall == 0.8
    assert metrics.f1 == 0.8


def test_prf1_zero_predictions_is_zero():
    metrics = prf1(tp=0, fp=0, fn=3)
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_confusion_counts_from_binary_lists():
    counts = confusion_counts([True, True, False, False], [True, False, True, False])
    assert counts == (1, 1, 1)


def test_temporal_iou_partial_overlap():
    pred = EventInterval("drop", 1.0, 3.0)
    truth = EventInterval("drop", 2.0, 5.0)
    assert abs(temporal_iou(pred, truth) - 1.0 / 4.0) < 1e-9


def test_temporal_iou_no_overlap_is_zero():
    assert temporal_iou(EventInterval("drop", 0.0, 1.0), EventInterval("drop", 2.0, 3.0)) == 0.0


def test_evaluate_events_tp_fp_fn():
    preds = [
        EventInterval("drop", 1.0, 2.0),
        EventInterval("drag", 5.0, 6.0),
    ]
    truths = [
        EventInterval("drop", 1.2, 2.2),
        EventInterval("throw", 8.0, 9.0),
    ]
    report = evaluate_events(preds, truths, iou_threshold=0.3)
    assert report.by_behaviour["drop"].tp == 1
    assert report.by_behaviour["drag"].fp == 1
    assert report.by_behaviour["throw"].fn == 1
    assert report.macro.precision > 0


def test_latency_mean_p50_p95():
    stats = summarize_latencies([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    assert isinstance(stats, LatencyStats)
    assert stats.mean == 55.0
    assert stats.p50 == 50.0
    assert stats.p95 == 100.0
    assert stats.count == 10


def test_latency_empty():
    stats = summarize_latencies([])
    assert stats.mean == 0.0
    assert stats.count == 0


def test_incidents_to_events():
    from handleguard.metrics.reports import incidents_to_events
    from handleguard.types import Incident, IncidentStatus, RiskLevel

    incidents = [
        Incident(
            incident_id="HG-0001",
            video_id="v1",
            behaviour="drop",
            risk_score=70,
            risk_level=RiskLevel.HIGH,
            confidence=0.8,
            start_time=1.0,
            end_time=2.0,
            primary_object_track="carton_1",
            actor_track=None,
            equipment_track=None,
            zone=None,
            evidence={},
            explanation="x",
            recommendation="y",
            status=IncidentStatus.NEW,
        )
    ]
    events = incidents_to_events(incidents)
    assert events == [EventInterval("drop", 1.0, 2.0)]
