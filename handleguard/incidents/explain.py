from __future__ import annotations

from handleguard.config.loader import AppConfig
from handleguard.risk.scorer import RiskResult
from handleguard.types import BehaviourEvidence


_TEMPLATES = {
    "drop": (
        "A product moved downward rapidly for {duration_s}s, followed by an abrupt stop. "
        "Estimated image-space drop displacement was {drop_distance_px} px "
        "(peak speed {peak_speed}). This pattern was classified as a potential drop event."
    ),
    "throw": (
        "A product showed high horizontal velocity ({horizontal_velocity} px/s) while unsupported. "
        "This pattern was classified as a potential throw/toss transfer."
    ),
    "drag": (
        "A product translated {distance_px} px horizontally near floor level with only "
        "{vertical_variation_px} px vertical variation over {duration_s}s. "
        "This pattern was classified as potential dragging."
    ),
    "rough_handling": (
        "A product exhibited an acceleration spike of {acceleration}. "
        "This was classified as potential rough handling, not confirmed damage."
    ),
    "improper_stack": (
        "Item {upper} sits above {lower} with overlap {overlap} and size ratio {size_ratio}. "
        "This stacking order violates the size/weight hierarchy heuristic."
    ),
    "unstable_stack": (
        "Upper item {child} has support ratio {support_ratio} on {support}. "
        "Low overlap indicates elevated slip/fall risk."
    ),
    "zone_violation": (
        "Product remained in zone '{zone}' ({zone_type}) for {duration_s}s, "
        "beyond the configured dwell threshold."
    ),
    "pallet_overhang": (
        "Product {product} is only {support_fraction} supported by pallet {pallet}. "
        "Overhang exceeds the configured support fraction."
    ),
    "stepping": (
        "A person track overlapped product {product} for {duration_s}s. "
        "This was classified as potential stepping/standing on product."
    ),
    "improper_manual_handling": (
        "A large product moved with {nearby_people} nearby person track(s) and no handling equipment in range."
    ),
    "unsafe_sequence": (
        "A large product was moved before approved handling equipment appeared in the scene."
    ),
    "unsafe_surface": (
        "A product moved through unsafe-surface zone '{zone}' for {duration_s}s."
    ),
}


def explain_incident(evidence: BehaviourEvidence, risk: RiskResult) -> str:
    template = _TEMPLATES.get(
        evidence.behaviour,
        "Observed behaviour '{behaviour}' with evidence {evidence}.",
    )
    payload = {
        "behaviour": evidence.behaviour,
        "evidence": evidence.evidence,
        **{k: evidence.evidence.get(k, "n/a") for k in (
            "duration_s",
            "drop_distance_px",
            "peak_speed",
            "horizontal_velocity",
            "distance_px",
            "vertical_variation_px",
            "acceleration",
            "upper",
            "lower",
            "overlap",
            "size_ratio",
            "child",
            "support",
            "support_ratio",
            "zone",
            "zone_type",
            "product",
            "pallet",
            "support_fraction",
            "nearby_people",
        )},
    }
    try:
        body = template.format(**payload)
    except (KeyError, ValueError):
        body = f"Observed behaviour '{evidence.behaviour}' with measured evidence {evidence.evidence}."
    return (
        f"{body} Risk {risk.score:.0f}/100 ({risk.level.value}); "
        f"confidence {risk.confidence:.2f}. This is decision support, not confirmed damage."
    )


def recommend_action(behaviour: str, config: AppConfig) -> str:
    return config.sop(behaviour)["recommendation"] or (
        "Review the event with a supervisor and follow the site SOP for this behaviour."
    )
