"""Rasterized circular calibration mesas, in integer nanometres."""
import math

import numpy as np


def _edges(low, high, pixel_nm):
    count = int(math.ceil((high - low) / pixel_nm))
    return np.rint(np.linspace(low, high, count + 1)).astype(np.int64)


def circle_union_rects(diameter_nm, separation_nm=0, pixel_nm=5):
    """Return disjoint RECTs for one circle or a horizontal equal-diameter dimer.

    The circle centre, or midpoint between the two centres, is (0, 0).
    ``separation_nm`` is the centre-to-centre distance, not the edge overlap.
    Pixel centres determine exposure; integer pixel edges are at most
    ``pixel_nm`` apart. Memory scales with diameter, not with exposed area.
    """
    if (not math.isfinite(diameter_nm) or diameter_nm <= 0
            or not math.isfinite(separation_nm) or separation_nm < 0
            or not math.isfinite(pixel_nm) or pixel_nm < 1
            or int(pixel_nm) != pixel_nm):
        raise ValueError("Require a positive diameter, nonnegative separation, and integer pixel >= 1 nm")

    radius = diameter_nm / 2
    x_edges = _edges(math.floor(-radius - separation_nm / 2),
                     math.ceil(radius + separation_nm / 2), pixel_nm)
    y_edges = _edges(math.floor(-radius), math.ceil(radius), pixel_nm)
    x_centres = (x_edges[:-1] + x_edges[1:]) / 2
    y_centres = (y_edges[:-1] + y_edges[1:]) / 2

    centres = (0,) if separation_nm == 0 else (-separation_nm / 2, separation_nm / 2)
    # Both circles have y=0, so their union in each x column is one interval.
    # Take the larger half-height before rasterization to avoid double exposure.
    squared_height = np.maximum.reduce([radius ** 2 - (x_centres - x) ** 2 for x in centres])
    height = np.sqrt(np.maximum(squared_height, 0))
    # searchsorted implements inclusive centre occupancy without allocating a
    # two-dimensional mask (a 36 um reference would contain 52 million pixels).
    lower = np.searchsorted(y_centres, -height, side="left")
    upper = np.searchsorted(y_centres, height, side="right")
    upper[squared_height < 0] = lower[squared_height < 0]

    rects = []
    start = 0
    for stop in range(1, len(x_centres) + 1):
        if stop < len(x_centres) and lower[stop] == lower[start] and upper[stop] == upper[start]:
            continue
        if upper[start] > lower[start]:
            rects.append((x_edges[start], y_edges[lower[start]],
                          x_edges[stop], y_edges[upper[start]]))
        start = stop
    return np.asarray(rects, dtype=np.int64).reshape(-1, 4)
