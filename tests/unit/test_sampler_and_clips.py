from __future__ import annotations

from handleguard.incidents.clips import ClipPlan, plan_clip
from handleguard.video.sampler import sample_timestamps


def test_sample_timestamps_skips_to_inference_fps():
    stamps = sample_timestamps(duration=1.0, source_fps=24.0, inference_fps=8.0)
    assert stamps[0] == 0.0
    assert stamps[1] == 0.125
    assert stamps[-1] < 1.0
    assert len(stamps) == 8


def test_sample_timestamps_uses_default_when_fps_missing():
    stamps = sample_timestamps(duration=1.0, source_fps=0.0, inference_fps=8.0)
    assert stamps[1] == 0.125


def test_sample_timestamps_rejects_non_positive_duration():
    assert sample_timestamps(duration=0, source_fps=24, inference_fps=8) == []


def test_plan_clip_adds_pre_and_post_buffer():
    plan = plan_clip(
        incident_id="HG-0001",
        start_time=4.2,
        end_time=4.8,
        video_duration=20.0,
        created_at="2026-09-04T00:00:00+00:00",
    )
    assert isinstance(plan, ClipPlan)
    assert plan.start_time == 1.2
    assert plan.end_time == 8.8
    assert plan.filename == "incident_20260904_HG-0001.mp4"


def test_plan_clip_clamps_to_video_bounds():
    plan = plan_clip(
        incident_id="HG-0002",
        start_time=1.0,
        end_time=1.5,
        video_duration=4.0,
        created_at="2026-09-04T00:00:00+00:00",
        pre_buffer=3.0,
        post_buffer=4.0,
    )
    assert plan.start_time == 0.0
    assert plan.end_time == 4.0
