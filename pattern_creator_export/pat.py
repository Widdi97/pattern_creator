"""Strict, non-executing import of the PAT subset emitted by pattern_creator.

Coordinates are interpreted as nanometres using the project Python convention;
PAT itself can use machine-calibrated pixels. D array fields are
dx, dy, nx, ny (generate_pattern.Lattice.generate_patterns). XPOLY and
YPOLY vertex order follows projects/ring_resonators_ecp/ring_resonators_ecp.py.
P type 0 is the RECT alias verified in XENOS ECP manual Appendix B.1.
Exposure increment/dwell are recorded, never interpreted as GDS geometry.
No CTL/stage commands or Python project files are executed.
"""

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import math
from pathlib import Path
import re

import gdstk
import numpy as np


INPUT_SCALE_ASSUMPTION = ("1 PAT coordinate interpreted as 1 nm based on project Python nm convention; "
                          "machine field calibration not inferred")


class PatError(ValueError):
    pass


@dataclass
class PatternDefinition:
    name: str
    line: int
    repetition: tuple | None = None
    metadata: dict = field(default_factory=dict)
    geometry: list = field(default_factory=list)


def parse_pat(text):
    """Parse complete D...END definitions; fail the whole input on ambiguity."""
    definitions, names = [], set()
    current = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        opcode, _, tail = line.partition(" ")
        opcode, tail = opcode.upper(), tail.strip()
        try:
            if opcode == "D":
                if current is not None:
                    raise PatError("D before preceding END")
                fields = [item.strip() for item in tail.split(",")]
                if len(fields) not in (1, 5) or not fields[0]:
                    raise PatError("D requires a name or name, dx, dy, nx, ny")
                if fields[0] in names:
                    raise PatError(f"duplicate definition {fields[0]!r}")
                names.add(fields[0])
                current = PatternDefinition(fields[0], number)
                if len(fields) == 5:
                    values = tuple(int(item) for item in fields[1:])
                    dx, dy, nx, ny = values
                    if not 1 <= nx <= 32767 or not 1 <= ny <= 32767:
                        raise PatError("array counts must lie in [1, 32767]")
                    if (nx > 1 and dx == 0) or (ny > 1 and dy == 0):
                        raise PatError("repeated direction has zero pitch")
                    current.repetition = values
            elif opcode == "END":
                if current is None or tail:
                    raise PatError("unmatched END or trailing data")
                if set(current.metadata) != {"I", "C"}:
                    raise PatError("each definition requires one I and one C")
                definitions.append(current)
                current = None
            elif opcode in ("I", "C"):
                if current is None or current.geometry or opcode in current.metadata:
                    raise PatError("misplaced or repeated exposure metadata")
                value = float(tail)
                if not math.isfinite(value) or value <= 0:
                    raise PatError("exposure metadata must be positive and finite")
                current.metadata[opcode] = value
            elif opcode in ("RECT", "CIRCLE", "XPOLY", "YPOLY", "P"):
                if current is None:
                    raise PatError("geometry outside a D...END definition")
                values = tuple(int(item.strip()) for item in tail.split(","))
                if opcode == "P":
                    if len(values) != 5 or values[0] != 0:
                        raise PatError("only verified P type 0 is supported: P 0, x0, y0, x1, y1")
                    opcode, values = "RECT", values[1:]
                count = {"RECT": 4, "CIRCLE": 3, "XPOLY": 6, "YPOLY": 6}[opcode]
                if len(values) != count:
                    raise PatError(f"{opcode} requires {count} integer coordinates")
                if opcode == "RECT" and (values[0] >= values[2] or values[1] >= values[3]):
                    raise PatError("RECT must have increasing corners and nonzero area")
                if opcode == "CIRCLE" and values[2] <= 0:
                    raise PatError("CIRCLE radius must be positive")
                if opcode in ("XPOLY", "YPOLY"):
                    points = polygon_points(opcode, values)
                    if polygon_twice_area(points) == 0:
                        raise PatError(f"degenerate {opcode}")
                    # Horizontal/vertical parallel edges may end in triangles,
                    # but their two widths must not have opposite signs.
                    a, b, c, d, e, f = values
                    widths = (c-a, d-e) if opcode == "XPOLY" else (c-b, d-f)
                    if widths[0] * widths[1] < 0:
                        raise PatError(f"self-crossing {opcode}")
                current.geometry.append((opcode, values, number))
            else:
                raise PatError(f"unsupported statement {opcode!r}")
        except (ValueError, OverflowError) as error:
            raise PatError(f"line {number}: {error}; {line[:160]}") from error
    if current is not None:
        raise PatError(f"line {current.line}: definition {current.name!r} has no END")
    if not definitions:
        raise PatError("no complete PAT definitions")
    return definitions


def polygon_points(opcode, values):
    a, b, c, d, e, f = values
    if opcode == "XPOLY":
        return [(a, b), (c, b), (d, f), (e, f)]
    return [(a, b), (a, c), (e, d), (e, f)]


def polygon_twice_area(points):
    return sum(x*y1-x1*y for (x, y), (x1, y1) in zip(points, points[1:]+points[:1]))


def _canonical(points):
    """Coordinate-exact signature, independent of hull start and direction."""
    points = [tuple(map(int, point)) for point in points]
    points = [p for i, p in enumerate(points) if p != points[i-1]]
    points = [p for i, p in enumerate(points)
              if (p[0]-points[i-1][0])*(points[(i+1) % len(points)][1]-p[1])
              != (p[1]-points[i-1][1])*(points[(i+1) % len(points)][0]-p[0])]
    if len(points) < 3:
        raise PatError("polygon collapses on the 1 nm GDS grid")
    forward = points[points.index(min(points)):] + points[:points.index(min(points))]
    reverse = list(reversed(points))
    reverse = reverse[reverse.index(min(reverse)):] + reverse[:reverse.index(min(reverse))]
    return tuple(min(forward, reverse))


def _cell_name(name, used):
    candidate = re.sub(r"[^A-Za-z0-9_$?]", "_", name)
    if candidate != name or len(candidate) > 32:
        candidate = candidate[:23] + "_" + hashlib.sha256(name.encode()).hexdigest()[:8]
    if candidate in used:
        raise PatError(f"GDS name collision for {name!r}")
    used.add(candidate)
    return candidate


def _role(name):
    match = re.search(r"_x_(-?1|0)_y_(-?1|0)$", name)
    if not match:
        return "unspecified"
    x, y = map(int, match.groups())
    return "corner" if x and y else "border" if x or y else "bulk"


def _polygons(opcode, values, tolerance_nm, layer):
    if opcode == "RECT":
        x0, y0, x1, y1 = values
        return [gdstk.rectangle((x0/1000, y0/1000), (x1/1000, y1/1000), layer=layer)]
    if opcode == "CIRCLE":
        x, y, radius = values
        poly = gdstk.ellipse((x/1000, y/1000), radius/1000,
                             tolerance=tolerance_nm/1000, layer=layer)
    else:
        poly = gdstk.Polygon(np.asarray(polygon_points(opcode, values))/1000, layer=layer)
    # Snap explicitly so the independent reader can verify every coordinate.
    poly = gdstk.Polygon(np.rint(poly.points*1000)/1000, layer=layer)
    return poly.fracture(max_points=199, precision=0.001)


def export_pat(definitions, destination, *, circle_tolerance_nm=1.0, layer=1):
    """Write separate pattern cells, preserving arrays; return validated ledger.

    The file is a library of named definitions, not an assembled wafer. Lattice
    bulk, individual borders, and individual corners remain separate cells.
    Input must be the complete definition list returned by parse_pat.
    """
    if not math.isfinite(circle_tolerance_nm) or circle_tolerance_nm <= 0:
        raise ValueError("circle_tolerance_nm must be positive and finite")
    if not isinstance(layer, int) or not 0 <= layer <= 65535:
        raise ValueError("layer must be an integer in [0, 65535]")
    library = gdstk.Library(unit=1e-6, precision=1e-9)
    used, expected, cells = set(), {}, []
    names = [_cell_name(definition.name, used) for definition in definitions]
    for index, (definition, name) in enumerate(zip(definitions, names)):
        named_cell = library.new_cell(name)
        motif = named_cell
        reference = None
        if definition.repetition:
            motif = library.new_cell(_cell_name(f"__PAT_MOTIF_{index}", used))
            dx, dy, nx, ny = definition.repetition
            if abs(dx*nx) >= 2**31 or abs(dy*ny) >= 2**31:
                raise PatError(f"line {definition.line}: array endpoint exceeds signed 32-bit nanometre range")
            named_cell.add(gdstk.Reference(motif, columns=nx, rows=ny, spacing=(dx/1000, dy/1000)))
            reference = {"cell": motif.name, "nx": nx, "ny": ny,
                         "dx_nm": dx if nx > 1 else 0, "dy_nm": dy if ny > 1 else 0}
            expected[name] = {"polygons": Counter(), "reference": reference}
        signatures = Counter()
        for opcode, values, line in definition.geometry:
            if opcode == "CIRCLE":
                x, y, radius = values
                bounds = ((x-radius, y-radius), (x+radius, y+radius))
            elif opcode == "RECT":
                bounds = (values[:2], values[2:])
            else:
                bounds = polygon_points(opcode, values)
            if any(abs(coord) >= 2**31 for point in bounds for coord in point):
                raise PatError(f"line {line}: source geometry exceeds signed 32-bit nanometre range")
            if definition.repetition and any(abs(coord+offset) >= 2**31 for point in bounds
                                             for coord, offset in zip(point, (dx*(nx-1), dy*(ny-1)))):
                raise PatError(f"line {line}: repeated source geometry exceeds signed 32-bit nanometre range")
            if opcode == "CIRCLE":
                # n >= pi / acos(1 - tolerance/radius); the equivalent asin
                # expression avoids cancellation for very fine tolerances.
                ratio = circle_tolerance_nm / (2*radius)
                angle = 2*math.asin(math.sqrt(min(1.0, ratio)))
                if angle == 0 or math.pi/angle > 1_000_000:
                    raise PatError(f"line {line}: circle tolerance requires more than 1000000 vertices; "
                                   "requested tolerance was not changed")
            for polygon in _polygons(opcode, values, circle_tolerance_nm, layer):
                key = _canonical(np.rint(polygon.points*1000).astype(np.int64))
                if any(abs(coord) >= 2**31 for point in key for coord in point):
                    raise PatError(f"line {line}: coordinate outside signed 32-bit nanometre range")
                if definition.repetition and any(abs(coord+offset) >= 2**31 for point in key
                                                 for coord, offset in zip(point, (dx*(nx-1), dy*(ny-1)))):
                    raise PatError(f"line {line}: repeated geometry exceeds signed 32-bit nanometre range")
                signatures[key] += 1
                motif.add(polygon)
        expected[motif.name] = {"polygons": signatures, "reference": None}
        cells.append({"source_name": definition.name, "gds_cell": name,
                      "geometry_cell": motif.name, "role_from_name": _role(definition.name),
                      "repetition": definition.repetition, "metadata": definition.metadata,
                      "geometry_counts": dict(Counter(item[0] for item in definition.geometry)),
                      "gds_polygon_count": sum(signatures.values())})
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".partial.gds")
    # Verify serialization with a different geometry library before replacing
    # the requested output. A validation error must not publish a partial file.
    try:
        library.write_gds(temporary, max_points=199)
        validation = validate_gds(temporary, expected, layer)
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {"scope": "independent PAT definition library; CTL/stage assembly not applied",
            "input_scale_assumption": INPUT_SCALE_ASSUMPTION,
            "unit_m": 1e-6, "precision_m": 1e-9, "layer": layer,
            "circle_chord_tolerance_nm": circle_tolerance_nm,
            "additional_grid_rounding_bound_nm": math.sqrt(0.5),
            "cells": cells, "validation": validation,
            "output_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            "output_bytes": destination.stat().st_size}


def validate_gds(path, expected, layer=1):
    """Check serialized polygons/references against the plan, not ideal curves."""
    import klayout.db as kdb

    layout = kdb.Layout()
    layout.read(str(path))
    if not math.isclose(layout.dbu, 0.001, abs_tol=1e-12):
        raise PatError(f"KLayout database unit mismatch: {layout.dbu}")
    actual = {cell.name: cell for cell in layout.each_cell()}
    if actual.keys() != expected.keys():
        raise PatError("KLayout cell-name set mismatch")
    polygons = references = 0
    for name, plan in expected.items():
        cell = actual[name]
        signatures = Counter()
        for index in layout.layer_indexes():
            info = layout.get_info(index)
            for shape in cell.shapes(index).each():
                if info.layer != layer or info.datatype != 0:
                    raise PatError(f"{name}: unexpected GDS layer/datatype")
                if not (shape.is_polygon() or shape.is_box() or shape.is_simple_polygon()):
                    raise PatError(f"{name}: unexpected GDS element")
                polygon = shape.polygon
                if polygon.holes():
                    raise PatError(f"{name}: unexpected polygon hole")
                signatures[_canonical([(p.x, p.y) for p in polygon.each_point_hull()])] += 1
        if signatures != plan["polygons"]:
            raise PatError(f"{name}: polygon-coordinate mismatch in KLayout readback")
        polygons += sum(signatures.values())
        instances = list(cell.each_inst())
        reference = plan["reference"]
        if len(instances) != int(reference is not None):
            raise PatError(f"{name}: reference-count mismatch")
        if reference:
            instance = instances[0]
            transform = instance.cplx_trans
            if (transform.angle != 0 or transform.is_mirror() or transform.mag != 1
                    or transform.disp.x != 0 or transform.disp.y != 0):
                raise PatError(f"{name}: reference transform mismatch")
            # KLayout may exchange the two equivalent AREF axes on import.
            observed_axes = sorted((vector.x, vector.y, count)
                                   for vector, count in ((instance.a, instance.na), (instance.b, instance.nb))
                                   if count > 1) if instance.is_regular_array() else []
            expected_axes = sorted((x, y, count)
                                   for x, y, count in ((reference["dx_nm"], 0, reference["nx"]),
                                                       (0, reference["dy_nm"], reference["ny"]))
                                   if count > 1)
            if instance.cell.name != reference["cell"] or observed_axes != expected_axes:
                raise PatError(f"{name}: array mismatch: {observed_axes!r} != {expected_axes!r}")
            references += 1
    return {"reader": "KLayout", "passed": True, "cells": len(actual),
            "polygon_coordinate_signatures_checked": polygons, "references_checked": references}
