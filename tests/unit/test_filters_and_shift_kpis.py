from __future__ import annotations

from datetime import datetime, timezone

from handleguard.metrics.kpis import ShiftKpis, high_risk_per_100, shift_kpis


def test_high_risk_per_100_handling_actions():
    rate = high_risk_per_100(high_risk_events=4, handling_actions=50)
    assert rate == 8.0


def test_high_risk_per_100_zero_actions():
    assert high_risk_per_100(high_risk_events=3, handling_actions=0) == 0.0


def test_shift_kpis_aggregates_counts():
    report = shift_kpis(
        total_incidents=20,
        high_risk=5,
        critical=2,
        false_positives=3,
        confirmed=8,
        handling_actions=100,
        mean_response_s=42.0,
    )
    assert isinstance(report, ShiftKpis)
    assert report.high_risk_events == 7
    assert report.false_positive_rate == 3 / 11
    assert report.high_risk_per_100 == 7.0
    assert report.mean_response_s == 42.0
    assert "intervention" in report.primary_kpi.lower()


def test_filter_incidents_by_bay_and_created_range():
    from handleguard.db.filters import incident_matches

    created = datetime(2026, 9, 8, 10, 0, tzinfo=timezone.utc)
    assert incident_matches(
        loading_bay="Bay-A",
        created_at=created,
        bay="Bay-A",
        start=datetime(2026, 9, 8, tzinfo=timezone.utc),
        end=datetime(2026, 9, 9, tzinfo=timezone.utc),
    )
    assert not incident_matches(
        loading_bay="Bay-B",
        created_at=created,
        bay="Bay-A",
        start=None,
        end=None,
    )
    assert not incident_matches(
        loading_bay="Bay-A",
        created_at=created,
        bay=None,
        start=datetime(2026, 9, 9, tzinfo=timezone.utc),
        end=None,
    )
