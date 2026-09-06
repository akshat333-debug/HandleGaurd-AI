#!/usr/bin/env python3
from __future__ import annotations

from handleguard.config.loader import load_config
from handleguard.db.repositories import save_incident, save_video
from handleguard.db.session import init_db, get_session
from handleguard.demo import DEMO_TIMELINE, demo_timestamps
from handleguard.pipeline import HandleGuardPipeline


def main() -> None:
    init_db()
    session = get_session()
    save_video(
        session,
        video_id="demo-bay-a",
        filename="demo_shift.mp4",
        source_type="synthetic",
        duration=12.0,
        fps=8.0,
        loading_bay="Bay-A",
        status="processed",
    )
    pipeline = HandleGuardPipeline.from_stub(
        DEMO_TIMELINE, config=load_config(), video_id="demo-bay-a"
    )
    result = pipeline.process_timeline(demo_timestamps())
    for incident in result.incidents:
        save_incident(session, incident)
    print(f"seeded {len(result.incidents)} incidents")
    session.close()


if __name__ == "__main__":
    main()
