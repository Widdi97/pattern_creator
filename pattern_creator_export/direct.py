"""Opt-in continuous-geometry export; never reads or edits legacy masks.

Inputs are nanometres and angles are radians. GDS uses micrometres with a
1 nm database grid. Curves are polygon approximations, not pixel contours.
Only support clipping and lattice half-step offsets depend on step_size.
Lattice geometry retains legacy site/half-step conventions. New GDS components
share a rounded 1 nm pitch and support, with corners aligned to their borders.
Geometry tests do not constitute fabrication-process qualification.
Source shapes outside the GDS coordinate range are rejected before clipping;
curve approximations requiring more than one million vertices are rejected.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import math
import re

import gdstk
import numpy as np


GRID_UM = 0.001
ROLES = {
    (0, 0): "BULK", (1, 0): "LEFT", (-1, 0): "RIGHT",
    (0, 1): "BOTTOM", (0, -1): "TOP",
    (1, 1): "CORNER_BL", (1, -1): "CORNER_TL",
    (-1, 1): "CORNER_BR", (-1, -1): "CORNER_TR",
}


@dataclass(frozen=True)
class ShapeSpec:
    """Ordered operation. Custom callables need explicit sample counts.

    lattice_margin_nm overrides the legacy max(args[2:]) site-selection
    heuristic; supply it explicitly for custom signatures without size args.
    """

    shape: object
    args: tuple
    boolean_operation: str
    samples: int | None = None
    lattice_margin_nm: float | None = None


def _positive(values, what):
    if not np.all(np.isfinite(values)) or np.any(np.asarray(values) <= 0):
        raise ValueError(f"{what} must be finite and positive")


def _step(step_size):
    value = np.asarray(step_size, dtype=float)
    if value.ndim == 0:
        value = np.repeat(value, 2)
    if value.shape != (2,):
        raise ValueError("step_size must be scalar or a pair")
    _positive(value, "step_size")
    return value


def _cell_name(name):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,31}", name):
        raise ValueError("GDS cell names must match [A-Za-z_][A-Za-z0-9_]{0,31}")
    return name


def _shape_polygon(spec, tolerance_nm):
    if spec.boolean_operation not in ("add", "subtract"):
        raise ValueError("boolean_operation must explicitly be 'add' or 'subtract'")
    args = spec.args
    if isinstance(spec.shape, str) and spec.shape in ("circle", "ellipse"):
        required = 3 if spec.shape == "circle" else 5
        if len(args) != required or not np.all(np.isfinite(args)):
            raise ValueError(f"{spec.shape} requires {required} finite numeric arguments")
        x, y = np.asarray(args[:2]) / 1000
        radii = np.asarray(args[2:3] if required == 3 else args[2:4]) / 1000
        _positive(radii, "radii")
        if required == 3:
            extent_x = extent_y = radii[0]
        else:
            c, s = math.cos(args[4]), math.sin(args[4])
            extent_x = math.hypot(radii[0] * c, radii[1] * s)
            extent_y = math.hypot(radii[0] * s, radii[1] * c)
        _check_coordinates(((x - extent_x, y - extent_y), (x + extent_x, y + extent_y)))
        ratio = tolerance_nm / (2000 * max(radii))
        angle = 2 * math.asin(math.sqrt(min(1.0, ratio)))
        if angle == 0 or math.pi / angle > 1_000_000:
            raise ValueError("curve tolerance requires more than 1000000 vertices; tolerance was not changed")
        p = gdstk.ellipse((x, y), radii[0] if required == 3 else tuple(radii),
                          tolerance=tolerance_nm / 1000)
        if required == 5:
            p.rotate(args[4], (x, y))
        return p
    if isinstance(spec.shape, str) and spec.shape == "polygon":
        if len(args) < 6 or len(args) % 2:
            raise ValueError("polygon requires at least three x,y pairs")
        points = np.asarray(args, dtype=float).reshape(-1, 2)
    elif callable(spec.shape):
        if not isinstance(spec.samples, int) or not 4 <= spec.samples <= 1_000_000:
            raise ValueError("custom curves require explicit integer samples between 4 and 1000000")
        points = np.asarray(spec.shape(np.linspace(0, 1, spec.samples), *args), dtype=float)
        if points.shape != (2, spec.samples):
            raise ValueError("custom curve must return (x, y), each of length samples")
        points = points.T
    else:
        raise ValueError(f"unsupported direct shape: {spec.shape!r}")
    if not np.all(np.isfinite(points)):
        raise ValueError("shape coordinates must be finite")
    _check_coordinates(points / 1000)
    result = gdstk.Polygon(points / 1000)
    if result.area() == 0:
        raise ValueError("shape has zero polygon area")
    return result


def _apply(polygons, shape, operation):
    return gdstk.boolean(polygons, [shape], "or" if operation == "add" else "not",
                         precision=GRID_UM)


def _support(size, step):
    # Legacy raster coordinates describe pixel centers. Keep their half-step
    # support at the boundary even though this path does not allocate pixels.
    count = np.asarray([int(size[i] / step[i]) for i in range(2)])
    if np.any(count < 1):
        raise ValueError("each pattern dimension must contain at least one sample")
    bounds = np.array([-step / 2, (count - 0.5) * step])
    return gdstk.rectangle(bounds[0] / 1000, bounds[1] / 1000), bounds


def _write(path, cells, layer, datatype):
    if any(not isinstance(v, int) or not 0 <= v <= 65535 for v in (layer, datatype)):
        raise ValueError("layer and datatype must be integers from 0 through 65535")
    for cell in cells:
        for polygon in cell.polygons:
            _check_coordinates(polygon.points)
            polygon.layer, polygon.datatype = layer, datatype
        for reference in cell.references:
            _check_coordinates(reference.origin)
            repetition = reference.repetition
            if repetition.spacing is not None:
                # AREF encodes full columns/rows endpoints, not just the last instance.
                _check_coordinates(np.asarray(reference.origin) + np.array([
                    [repetition.columns * repetition.spacing[0], 0],
                    [0, repetition.rows * repetition.spacing[1]]]))
            bounds = reference.bounding_box()
            if bounds is not None:
                _check_coordinates(bounds)
    library = gdstk.Library(unit=1e-6, precision=1e-9)
    library.add(*cells)
    library.write_gds(str(Path(path)), max_points=199, timestamp=datetime(2000, 1, 1))


def _check_coordinates(coordinates_um):
    grid = np.rint(np.asarray(coordinates_um) / GRID_UM)
    if not np.all(np.isfinite(grid)) or np.any(grid < -(2**31)) or np.any(grid > 2**31 - 1):
        raise ValueError("GDS geometry or array exceeds signed 32-bit coordinates at 1 nm precision")


class DirectPattern:
    """Ordered continuous shapes clipped to the legacy Pattern support, in nm."""
    def __init__(self, x_size, y_size, step_size, pattern_name="PATTERN", *, tolerance_nm=1):
        _positive((x_size, y_size, tolerance_nm), "sizes and tolerance_nm")
        self.pattern_name = _cell_name(pattern_name)
        self.tolerance_nm = tolerance_nm
        self.step_size = _step(step_size)
        self.clip, self.support_nm = _support((x_size, y_size), self.step_size)
        self.operations = []

    def add_parametrized_shape(self, shape, *args, boolean_operation, samples=None):
        """Record an explicit operation; no history is inferred from legacy shapes."""
        spec = ShapeSpec(shape, tuple(args), boolean_operation, samples)
        _shape_polygon(spec, self.tolerance_nm)  # Fail when added, before creating a file.
        self.operations.append(spec)
        return self

    def export_gds(self, path, *, layer=1, datatype=0):
        """Write polygons and return metadata; independent readback is caller-owned."""
        polygons = []
        for spec in self.operations:
            polygons = _apply(polygons, _shape_polygon(spec, self.tolerance_nm),
                              spec.boolean_operation)
        polygons = gdstk.boolean(polygons, [self.clip], "and", precision=GRID_UM)
        cell = gdstk.Cell(self.pattern_name)
        cell.add(*polygons)
        _write(path, [cell], layer, datatype)
        return {"mode": "direct_parametric", "unit_m": 1e-6, "precision_m": 1e-9,
                "support_nm": self.support_nm.tolist(), "tolerance_nm": self.tolerance_nm,
                "difference_from_raster": "Continuous polygons clipped to legacy pixel support; not mask-equivalent."}


class DirectLattice:
    """Direct counterpart of the supported axis-aligned legacy lattice path.

    Shapes and basis vectors pair by index. Explicit operations execute per
    site in i,j,basis order; unlike legacy Lattice, they can include subtraction.
    The inherited site search is deliberately [-25,24]^2.
    The nine cell roles refer to source k/l; corner placement aligns with edges.
    Counts floor x_size/Ax and y_size/Ay just as the legacy text writer does.
    """

    def __init__(self, a1, a2, x_size, y_size, max_step_size, shapes, b_vecs,
                 pattern_name="LATTICE", global_offsetx=0, global_offsety=0, *, tolerance_nm=1):
        self.a1, self.a2 = np.asarray(a1, dtype=float), np.asarray(a2, dtype=float)
        if self.a1.shape != (2,) or self.a2.shape != (2,) or not np.all(np.isfinite([self.a1, self.a2])):
            raise ValueError("lattice vectors must be finite pairs")
        if self.a1[1] != 0 or self.a1[0] <= 0 or self.a2[1] <= 0:
            raise ValueError("legacy placement requires a1 parallel to +x and a2.y > 0")
        _positive((x_size, y_size, tolerance_nm), "sizes and tolerance_nm")
        for ny in range(1, 20):
            my = -ny * self.a2[0] / self.a1[0]
            if abs(round(my) - my) < 1e-4:
                break
        else:
            raise ValueError("no legacy rectangular supercell within 19 steps")
        self.period_nm = np.array([self.a1[0], ny * self.a2[1]])
        max_step = min(_step(max_step_size))
        self.step_size = self.period_nm / np.ceil(self.period_nm / max_step)
        self.counts = np.array([x_size // self.period_nm[0], y_size // self.period_nm[1]], dtype=int)
        self.array_pitch_nm = np.rint(self.period_nm).astype(int)
        _positive(self.array_pitch_nm, "rounded integer array pitch")
        # Clip widths, repeats and border positions share one integer pitch so
        # rounding a fractional period cannot accumulate gaps along an array.
        lower = np.rint(-self.step_size / 2)
        self.support_nm = np.array([lower, lower + self.array_pitch_nm])
        self.clip = gdstk.rectangle(self.support_nm[0] / 1000, self.support_nm[1] / 1000)
        if np.any(self.counts < 1) or np.any(self.counts > 32767):
            raise ValueError("legacy array counts must be between 1 and 32767")
        self.pattern_name = _cell_name(pattern_name)
        for role in ROLES.values():
            _cell_name(pattern_name + "_" + role)
        self.shapes = tuple(shapes)
        self.b_vecs = np.asarray(b_vecs, dtype=float)
        if self.b_vecs.shape != (len(self.shapes), 2) or not np.all(np.isfinite(self.b_vecs)):
            raise ValueError("b_vecs must have one finite (x,y) pair per ShapeSpec")
        self.offset_nm = np.asarray([global_offsetx, global_offsety], dtype=float)
        if not np.all(np.isfinite(self.offset_nm)):
            raise ValueError("global offsets must be finite")
        self.tolerance_nm = tolerance_nm
        self.polygons = [_shape_polygon(spec, tolerance_nm) for spec in self.shapes]
        self.margins = []
        for spec in self.shapes:
            margin = spec.lattice_margin_nm
            if margin is None:
                if len(spec.args) < 3:
                    raise ValueError("custom lattice shape requires lattice_margin_nm")
                margin = max(spec.args[2:])
            if not np.isscalar(margin) or not math.isfinite(margin) or margin < 0:
                raise ValueError("lattice site margin must be finite and nonnegative")
            self.margins.append(margin)

    def export_gds(self, path, *, layer=1, datatype=0):
        """Write a top cell and all nine separate components; return their mapping."""
        geometry = {key: [] for key in ROLES}
        for i in range(-25, 25):
            for j in range(-25, 25):
                for basis, spec, polygon, margin in zip(self.b_vecs, self.shapes, self.polygons, self.margins):
                    site = i * self.a1 + j * self.a2 + basis
                    tol = max(self.period_nm) * 1e-7 + margin
                    if np.all(site >= -tol) and np.all(site <= self.period_nm + tol):
                        for key in ROLES:
                            shift = site + np.asarray(key) * self.period_nm - self.step_size / 2
                            shape = polygon.copy().translate(*(shift / 1000))
                            geometry[key] = _apply(geometry[key], shape, spec.boolean_operation)
        top = gdstk.Cell(self.pattern_name)
        cells, metadata = [top], []
        countx, county = self.counts
        base = np.rint(2 * self.period_nm + self.offset_nm)
        px, py = self.array_pitch_nm
        for (k, l), role in ROLES.items():
            cell = gdstk.Cell(self.pattern_name + "_" + role)
            cell.add(*gdstk.boolean(geometry[k, l], [self.clip], "and", precision=GRID_UM))
            cells.append(cell)
            # The legacy writer adds another +Ay to corners. New GDS corners
            # instead meet their border endpoints; the PAT writer is untouched.
            offset = base + np.array([-px if k == 1 else countx * px if k == -1 else 0,
                                      -py if l == 1 else county * py if l == -1 else 0])
            columns, rows = (int(countx) if k == 0 else 1), (int(county) if l == 0 else 1)
            top.add(gdstk.Reference(cell, origin=offset / 1000, columns=columns, rows=rows,
                                    spacing=self.array_pitch_nm / 1000))
            metadata.append({"role": role, "cell": cell.name, "source_k": k, "source_l": l,
                             "origin_nm": offset.tolist(), "columns": columns, "rows": rows,
                             "polygon_count": len(cell.polygons)})
        _write(path, cells, layer, datatype)
        return {"mode": "direct_parametric_lattice", "placement": "aligned_grid_components",
                "source_difference": "New GDS uses nearest-nm pitch and abutting support; corner +Ay removed; old PAT unchanged",
                "process_qualified": False, "unit_m": 1e-6, "precision_m": 1e-9,
                "period_nm": self.period_nm.tolist(), "support_nm": self.support_nm.tolist(),
                "array_pitch_nm": self.array_pitch_nm.tolist(),
                "step_size_nm": self.step_size.tolist(), "counts": self.counts.tolist(),
                "tolerance_nm": self.tolerance_nm, "site_index_range": [-25, 24], "cells": metadata,
                "difference_from_raster": "Continuous polygons; legacy site search and half-step shift retained, support snapped to common pitch."}
