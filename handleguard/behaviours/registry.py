from __future__ import annotations

from handleguard.behaviours.base import BehaviourDetector
from handleguard.behaviours.drag import DragDetector
from handleguard.behaviours.drop import DropDetector
from handleguard.behaviours.improper_manual_handling import ImproperManualHandlingDetector
from handleguard.behaviours.improper_stack import ImproperStackDetector
from handleguard.behaviours.pallet_overhang import PalletOverhangDetector
from handleguard.behaviours.rough_handling import RoughHandlingDetector
from handleguard.behaviours.stepping import SteppingDetector
from handleguard.behaviours.throw import ThrowDetector
from handleguard.behaviours.unsafe_sequence import UnsafeSequenceDetector
from handleguard.behaviours.unsafe_surface import UnsafeSurfaceDetector
from handleguard.behaviours.unstable_stack import UnstableStackDetector
from handleguard.behaviours.zone_violation import ZoneViolationDetector


def build_detectors() -> list[BehaviourDetector]:
    return [
        ZoneViolationDetector(),
        DragDetector(),
        DropDetector(),
        PalletOverhangDetector(),
        UnstableStackDetector(),
        ImproperStackDetector(),
        RoughHandlingDetector(),
        ThrowDetector(),
        SteppingDetector(),
        ImproperManualHandlingDetector(),
        UnsafeSequenceDetector(),
        UnsafeSurfaceDetector(),
    ]
