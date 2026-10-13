"""Exact KPZ inputs and finite, separately addressable ECP lattice components.

Input lengths are micrometres; every returned rectangle and repetition is in
integer nanometres. Mesas are the exposed Boolean union of implicit ellipses.
The raster is a documented approximation, independent of the solver's grid.
"""
import json
import math
from pathlib import Path
import re

import numpy as np


ROLES = ("bulk", "left", "right", "bottom", "top", "bl", "br", "tl", "tr")
_ROLE_AXES = ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (1, -1), (-1, 1), (1, 1))


def parse_report(path):
    """Read all full-precision geometry records; never execute report text."""
    text = Path(path).read_text(encoding="utf-8-sig")
    section = text.split("FULL-PRECISION GEOMETRY RECORDS: ALL 20 UNIQUE LATTICES", 1)[1]
    section = section.split("ALL CENTER DESCRIPTORS:", 1)[0]
    records = []
    for match in re.finditer(r"^GEOMETRY (\S+)\r?\n(.*?)(?=^GEOMETRY |\Z)",
                             section, flags=re.M | re.S):
        record = {"geometry_id": match.group(1)}
        for line in match.group(2).splitlines():
            if " = " not in line:
                continue
            key, value = line.split(" = ", 1)
            if key == "Set memberships":
                record["memberships"] = value.split(", ")
            else:
                record[key] = json.loads(value)
        records.append(record)
    memberships = [m for r in records for m in r["memberships"]]
    if (len(records) != 20 or len({r["geometry_id"] for r in records}) != 20
            or sorted(memberships) != [f"{s}{n}" for s in "ABC" for n in range(1, 9)]):
        raise ValueError("Expected 20 unique geometries and each A1-C8 membership once")
    return records


def _edges(low, high, pixel_nm):
    # The endpoints are shared exact midplanes. Rounding interior grid points
    # gives integer writer coordinates without accumulating a period error.
    count = int(math.ceil((high - low) / pixel_nm))
    edges = np.rint(np.linspace(low, high, count + 1)).astype(np.int64)
    if np.any(np.diff(edges) <= 0) or np.max(np.diff(edges)) > pixel_nm:
        raise ValueError("Pixel size must permit a nonzero integer grid")
    return edges


def _axis_grid(side, pitch, halfwidth, pixel):
    if side == 0:
        return _edges(-pitch // 2, pitch // 2, pixel)
    left = _edges(-math.ceil(halfwidth), pitch // 2, pixel)
    return left if side < 0 else -left[::-1]


def _mask_rectangles(mask, xedges, yedges):
    """Merge equal vertical runs across columns without changing their union."""
    rects, start, previous = [], 0, None
    for col in range(mask.shape[1] + 1):
        if col == mask.shape[1]:
            runs = None
        else:
            transitions = np.flatnonzero(np.diff(np.r_[False, mask[:, col], False]))
            runs = tuple(zip(transitions[::2], transitions[1::2]))
        if runs != previous:
            if previous:
                rects.extend((xedges[start], yedges[a], xedges[col], yedges[b])
                             for a, b in previous)
            start, previous = col, runs
    return np.asarray(rects, dtype=np.int64).reshape(-1, 4)


def build_device(record, size_nm=90_000, pixel_nm=5):
    """Build a whole-mesa finite patch, bounded by ``size_nm`` in both axes.

    Nine components partition the patch at nearest-neighbor midplanes. Bulk
    repeats in two axes; borders repeat along one axis; corners are single.
    Exterior cells preserve rounded caps and contain no fictitious neighbors.
    Return structures as ``(role, rects, (dx, dy, nx, ny) or None)``. Rectangles
    already include each component's local-device placement, with the first
    mesa centered at (0, 0). Repetition translates only these base rectangles.
    """
    a1, a2 = record["lattice_a1_um"], record["lattice_a2_um"]
    if a1[1] != 0 or a2[0] != 0 or record["basis_centers_um"] != [[0.0, 0.0]]:
        raise ValueError("Expected an axis-aligned, single-mesa rectangular lattice")
    periods = np.array([a1[0], a2[1]]) * 1000
    ax, ay = np.rint(periods).astype(np.int64)
    if (min(ax, ay) <= 0 or ax % 2 or ay % 2
            or not np.allclose(periods, [ax, ay], rtol=0, atol=1e-6)):
        raise ValueError("The catalogue requires positive even integer-nm periods")
    if not math.isfinite(pixel_nm) or not 1 <= pixel_nm <= 5 or pixel_nm != int(pixel_nm):
        raise ValueError("Use an integer raster step between 1 and 5 nm")
    major = float(record["major_semiaxis_um"]) * 1000
    minor = float(record["minor_semiaxis_um"]) * 1000
    angle = record["rotation_deg_ccw"]
    if angle not in (0, 90) or not np.isfinite([major, minor, size_nm]).all() or min(major, minor, size_nm) <= 0:
        raise ValueError("Expected positive dimensions and a 0 or 90 degree ellipse")
    # For the catalogue's two orientations, swapping axes avoids trigonometric
    # roundoff at 90 degrees and makes reflected devices exactly symmetric.
    hx, hy = (major, minor) if angle == 0 else (minor, major)
    nx = math.floor((size_nm - 2 * hx) / ax + 1e-12) + 1
    ny = math.floor((size_nm - 2 * hy) / ay + 1e-12) + 1
    if min(nx, ny) < 3:
        raise ValueError("The finite patch must contain at least 3 mesas per axis")
    structures, boxes = [], {}
    for role, (sx, sy) in zip(ROLES, _ROLE_AXES):
        ix = 0 if sx < 0 else nx - 1 if sx > 0 else 1
        iy = 0 if sy < 0 else ny - 1 if sy > 0 else 1
        xedges = _axis_grid(sx, int(ax), hx, pixel_nm)
        yedges = _axis_grid(sy, int(ay), hy, pixel_nm)
        x = (xedges[:-1] + xedges[1:]) / 2
        y = (yedges[:-1] + yedges[1:]) / 2
        mask = np.zeros((len(y), len(x)), dtype=bool)
        # Rasterize the union before rectangle decomposition. This avoids any
        # double exposure where adjacent mesas overlap, including at tile seams.
        mx, my = math.ceil(hx / ax), math.ceil(hy / ay)
        for dx in range(-mx, mx + 1):
            for dy in range(-my, my + 1):
                if 0 <= ix + dx < nx and 0 <= iy + dy < ny:
                    mask |= (((x[None, :] - dx * ax) / hx) ** 2
                             + ((y[:, None] - dy * ay) / hy) ** 2 <= 1)
        rects = _mask_rectangles(mask, xedges, yedges)
        rects += np.array([ix * ax, iy * ay, ix * ax, iy * ay])
        columns, rows = (nx - 2 if sx == 0 else 1), (ny - 2 if sy == 0 else 1)
        repeat = (int(ax), int(ay), columns, rows) if columns > 1 or rows > 1 else None
        structures.append((role, rects, repeat))
        boxes[role] = [int(xedges[0] + ix * ax), int(yedges[0] + iy * ay),
                       int(xedges[-1] + ix * ax), int(yedges[-1] + iy * ay)]
    lower, upper, area = [], [], 0
    for _, rects, repeat in structures:
        if len(rects):
            dx, dy, columns, rows = repeat or (0, 0, 1, 1)
            lower.append(rects[:, :2].min(0))
            upper.append(rects[:, 2:].max(0) + [dx * (columns - 1), dy * (rows - 1)])
            area += int(np.prod(rects[:, 2:] - rects[:, :2], axis=1).sum()) * columns * rows
    # Measure the actual written separation on each mesa-center line. This is
    # especially important for B4 and A7, whose analytic gaps are only 10-13 nm.
    # Connected neighbors have zero open gap (negative analytic gaps mean overlap).
    bulk = structures[0][1]
    horizontal = bulk[(bulk[:, 1] <= ay) & (bulk[:, 3] > ay)]
    vertical = bulk[(bulk[:, 0] <= ax) & (bulk[:, 2] > ax)]
    written_gaps = [int(ax - (horizontal[:, 2].max() - horizontal[:, 0].min())),
                    int(ay - (vertical[:, 3].max() - vertical[:, 1].min()))]
    return {"nx": nx, "ny": ny, "ax_nm": int(ax), "ay_nm": int(ay),
            "halfwidths_nm": [hx, hy], "pixel_nm": int(pixel_nm),
            "analytic_bbox_nm": [-hx, -hy, (nx - 1) * ax + hx, (ny - 1) * ay + hy],
            "written_bbox_nm": [*np.min(lower, axis=0).tolist(), *np.max(upper, axis=0).tolist()],
            "written_centerline_gaps_nm": written_gaps,
            "nominal_axial_gaps_nm": [ax - 2 * hx, ay - 2 * hy],
            "exposed_area_nm2": area, "structures": structures, "role_boxes_nm": boxes,
            "record": record}
