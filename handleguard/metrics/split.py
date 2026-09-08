from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True, slots=True)
class ClipRecord:
    video_id: str
    session_id: str
    behaviour: str


@dataclass
class DatasetSplit:
    train: list[ClipRecord]
    val: list[ClipRecord]
    test: list[ClipRecord]


def leakage_safe_split(
    clips: list[ClipRecord],
    train: float = 0.7,
    val: float = 0.15,
    test: float = 0.15,
    seed: int = 0,
) -> DatasetSplit:
    grouped: dict[str, list[ClipRecord]] = {}
    for clip in clips:
        grouped.setdefault(clip.session_id, []).append(clip)
    sessions = list(grouped.keys())
    Random(seed).shuffle(sessions)
    n = len(sessions)
    n_train = max(1, round(n * train)) if n else 0
    n_val = round(n * val) if n else 0
    if n_train + n_val >= n and n > 1:
        n_val = max(0, n - n_train - 1)
    train_ids = set(sessions[:n_train])
    val_ids = set(sessions[n_train : n_train + n_val])
    test_ids = set(sessions[n_train + n_val :])
    return DatasetSplit(
        train=[c for sid in train_ids for c in grouped[sid]],
        val=[c for sid in val_ids for c in grouped[sid]],
        test=[c for sid in test_ids for c in grouped[sid]],
    )
