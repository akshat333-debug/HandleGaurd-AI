from __future__ import annotations

from handleguard.features.geometry import (
    bbox_area,
    bbox_bottom_center,
    bbox_center,
    distance,
    horizontal_overlap,
    intersection_area,
    iou,
    point_in_polygon,
    relative_position,
    support_fraction,
    support_ratio,
    vertical_gap,
)


def test_bbox_center_midpoint():
    assert bbox_center((0, 0, 10, 20)) == (5.0, 10.0)


def test_bbox_bottom_center():
    assert bbox_bottom_center((0, 0, 10, 20)) == (5.0, 20.0)


def test_bbox_area():
    assert bbox_area((0, 0, 10, 5)) == 50.0


def test_iou_identical_boxes_is_one():
    box = (10, 10, 30, 40)
    assert iou(box, box) == 1.0


def test_iou_no_overlap_is_zero():
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_intersection_partial_overlap():
    assert intersection_area((0, 0, 10, 10), (5, 5, 15, 15)) == 25.0


def test_horizontal_overlap_ratio():
    assert horizontal_overlap((0, 0, 10, 10), (5, 0, 15, 10)) == 0.5


def test_vertical_gap_when_stacked():
    upper = (0, 0, 10, 10)
    lower = (0, 20, 10, 30)
    assert vertical_gap(upper, lower) == 10.0


def test_distance():
    assert distance((0, 0), (3, 4)) == 5.0


def test_point_in_polygon_inside():
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert point_in_polygon((5, 5), square) is True


def test_point_in_polygon_outside():
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert point_in_polygon((15, 5), square) is False


def test_support_ratio_and_fraction():
    child = (10, 0, 30, 10)
    support = (0, 10, 20, 20)
    assert support_ratio(child, support) == 0.5
    product = (0, 0, 10, 10)
    pallet = (0, 0, 5, 10)
    assert support_fraction(product, pallet) == 0.5


def test_relative_position_flags_above():
    result = relative_position((0, 0, 10, 10), (0, 20, 10, 30))
    assert result["a_above_b"] is True
    assert result["dy"] < 0
