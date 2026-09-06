from __future__ import annotations

from math import hypot

from handleguard.types import BBox, Point, Polygon


def _validate_bbox(box: BBox) -> BBox:
    x1, y1, x2, y2 = box
    if x2 < x1:
        x1, x2 = x2, x1
    if y2 < y1:
        y1, y2 = y2, y1
    return (float(x1), float(y1), float(x2), float(y2))


def bbox_center(box: BBox) -> Point:
    x1, y1, x2, y2 = _validate_bbox(box)
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def bbox_bottom_center(box: BBox) -> Point:
    x1, _, x2, y2 = _validate_bbox(box)
    return ((x1 + x2) / 2.0, float(y2))


def bbox_area(box: BBox) -> float:
    x1, y1, x2, y2 = _validate_bbox(box)
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def bbox_size(box: BBox) -> tuple[float, float]:
    x1, y1, x2, y2 = _validate_bbox(box)
    return (max(0.0, x2 - x1), max(0.0, y2 - y1))


def intersection_area(a: BBox, b: BBox) -> float:
    ax1, ay1, ax2, ay2 = _validate_bbox(a)
    bx1, by1, bx2, by2 = _validate_bbox(b)
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    return max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)


def iou(a: BBox, b: BBox) -> float:
    inter = intersection_area(a, b)
    if inter <= 0:
        return 0.0
    union = bbox_area(a) + bbox_area(b) - inter
    if union <= 0:
        return 0.0
    return inter / union


def horizontal_overlap(a: BBox, b: BBox) -> float:
    ax1, _, ax2, _ = _validate_bbox(a)
    bx1, _, bx2, _ = _validate_bbox(b)
    overlap = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    width_a = max(0.0, ax2 - ax1)
    if width_a == 0:
        return 0.0
    return overlap / width_a


def vertical_gap(a: BBox, b: BBox) -> float:
    """Positive when a is fully above b (smaller y2 than b.y1). Image y grows down."""
    _, ay1, _, ay2 = _validate_bbox(a)
    _, by1, _, by2 = _validate_bbox(b)
    if ay2 <= by1:
        return by1 - ay2
    if by2 <= ay1:
        return ay1 - by2
    return 0.0


def distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def relative_position(a: BBox, b: BBox) -> dict[str, float | bool]:
    ac = bbox_center(a)
    bc = bbox_center(b)
    return {
        "dx": ac[0] - bc[0],
        "dy": ac[1] - bc[1],
        "distance": distance(ac, bc),
        "a_above_b": ac[1] < bc[1],
    }


def point_in_polygon(point: Point, polygon: Polygon) -> bool:
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def support_ratio(child: BBox, support: BBox) -> float:
    """Horizontal overlap of child vs support, divided by child width."""
    return horizontal_overlap(child, support)


def support_fraction(product: BBox, pallet: BBox) -> float:
    area = bbox_area(product)
    if area <= 0:
        return 0.0
    return intersection_area(product, pallet) / area
