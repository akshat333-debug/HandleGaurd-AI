from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from handleguard.features.geometry import bbox_bottom_center, distance, iou
from handleguard.types import TrackState, is_equipment, is_pallet, is_person, is_product


@dataclass(slots=True)
class Interaction:
    source: str
    target: str
    relation: str
    score: float


@dataclass
class EventGraph:
    timestamp: float = 0.0
    tracks: dict[str, TrackState] = field(default_factory=dict)
    interactions: list[Interaction] = field(default_factory=list)

    def products(self) -> list[TrackState]:
        return [t for t in self.tracks.values() if is_product(t.class_name)]

    def people(self) -> list[TrackState]:
        return [t for t in self.tracks.values() if is_person(t.class_name)]

    def equipment(self) -> list[TrackState]:
        return [t for t in self.tracks.values() if is_equipment(t.class_name)]

    def pallets(self) -> list[TrackState]:
        return [t for t in self.tracks.values() if is_pallet(t.class_name)]

    def related(self, track_id: str, relation: str | None = None) -> list[str]:
        out = []
        for item in self.interactions:
            if relation and item.relation != relation:
                continue
            if item.source == track_id:
                out.append(item.target)
            elif item.target == track_id:
                out.append(item.source)
        return out


def build_event_graph(
    tracks: Iterable[TrackState],
    timestamp: float,
    associate_px: float = 80.0,
) -> EventGraph:
    track_list = list(tracks)
    graph = EventGraph(
        timestamp=timestamp,
        tracks={t.track_id: t for t in track_list},
    )
    products = [t for t in track_list if is_product(t.class_name)]
    people = [t for t in track_list if is_person(t.class_name)]
    equipment = [t for t in track_list if is_equipment(t.class_name)]
    pallets = [t for t in track_list if is_pallet(t.class_name)]

    for person in people:
        for product in products:
            d = distance(bbox_bottom_center(person.bbox), bbox_bottom_center(product.bbox))
            if d <= associate_px:
                graph.interactions.append(
                    Interaction(person.track_id, product.track_id, "handling", 1.0 - d / associate_px)
                )
                product.related_tracks.append(person.track_id)
                person.related_tracks.append(product.track_id)

    for product in products:
        for pallet in pallets:
            overlap = iou(product.bbox, pallet.bbox)
            if overlap >= 0.05:
                graph.interactions.append(
                    Interaction(product.track_id, pallet.track_id, "supported_by", overlap)
                )

    for eq in equipment:
        for product in products:
            d = distance(bbox_bottom_center(eq.bbox), bbox_bottom_center(product.bbox))
            if d <= associate_px * 2:
                graph.interactions.append(
                    Interaction(eq.track_id, product.track_id, "equipment_nearby", 1.0)
                )

    for i, a in enumerate(products):
        for b in products[i + 1 :]:
            overlap = iou(a.bbox, b.bbox)
            stacked = a.bbox[3] <= b.bbox[1] + 12 or b.bbox[3] <= a.bbox[1] + 12
            if overlap >= 0.05 or stacked:
                graph.interactions.append(Interaction(a.track_id, b.track_id, "stacked", overlap))

    return graph
