from __future__ import annotations


def pixels_to_metres(pixels: float, metres_per_pixel: float | None) -> float | None:
    if metres_per_pixel is None or metres_per_pixel <= 0:
        return None
    return round(pixels * metres_per_pixel, 3)


def describe_drop(pixels: float, metres_per_pixel: float | None = None) -> str:
    metres = pixels_to_metres(pixels, metres_per_pixel)
    if metres is None:
        return f"{pixels:.0f} px vertical drop proxy."
    return f"estimated ~{metres:.2f} m under calibrated scene geometry"
