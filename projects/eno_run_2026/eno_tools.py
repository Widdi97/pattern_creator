"""Shared helpers for the etch-and-overgrow (EnO) run 2026 e-beam patterns.

All lengths are in nm (ECP pattern units). Shapes are rasterised on a square
pixel grid and converted into RECT strips (one strip per pixel column, merged
with identical neighbouring columns), the same strategy as
``rectangulize_oli_horizontal_grouping`` in ``rectangulize.py`` but vectorised.

Shapes are tuples
    ("circle", x, y, d)
    ("ellipse", x, y, dx, dy, phi_deg)     full axes dx, dy before rotation
    ("polygon", [[x0, y0], [x1, y1], ...])
    ("rect", x1, y1, x2, y2)
    ("compound", [shapes])                 evaluated on its own, then OR'ed
Any shape tuple may be wrapped as ("subtract", shape) to cut it out of
everything added before it in the same list. Use "compound" when a cut must
only act on one well (e.g. the hole of an s-well next to a touching neighbour),
which is how the GPE drivers build their per-atom masks.
"""
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.path import Path

PIXEL_NM = 25       # raster step, same as the 2024 EnO run
INCREMENT = 16      # ECP increment used for all 2024 EnO lattices
DWELL_NS = 100      # ECP dwell time used for all 2024 EnO lattices
FIELD_NM = 500_000  # usable write-field coordinate range in the 2024 EnO pat files


# --------------------------------------------------------------------- shapes
def shape_bbox(shape):
    kind = shape[0]
    if kind == "subtract":
        return shape_bbox(shape[1])
    if kind == "circle":
        _, x, y, d = shape
        return x - d / 2, y - d / 2, x + d / 2, y + d / 2
    if kind == "ellipse":
        _, x, y, dx, dy, phi = shape
        c, s = np.cos(np.radians(phi)), np.sin(np.radians(phi))
        hx = np.hypot(dx / 2 * c, dy / 2 * s)
        hy = np.hypot(dx / 2 * s, dy / 2 * c)
        return x - hx, y - hy, x + hx, y + hy
    if kind == "polygon":
        p = np.asarray(shape[1], dtype=float)
        return p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()
    if kind == "rect":
        return shape[1:5]
    if kind == "compound":
        return shapes_bbox(shape[1])
    raise ValueError(f"unknown shape {kind}")


def _inside(shape, X, Y):
    kind = shape[0]
    if kind == "compound":
        out = np.zeros(X.shape, dtype=bool)
        for s in shape[1]:
            if s[0] == "subtract":
                out &= ~_inside(s[1], X, Y)
            else:
                out |= _inside(s, X, Y)
        return out
    if kind == "circle":
        _, x, y, d = shape
        return (X - x) ** 2 + (Y - y) ** 2 < (d / 2) ** 2
    if kind == "ellipse":
        _, x, y, dx, dy, phi = shape
        c, s = np.cos(np.radians(phi)), np.sin(np.radians(phi))
        u = (X - x) * c + (Y - y) * s
        v = -(X - x) * s + (Y - y) * c
        return (u / (dx / 2)) ** 2 + (v / (dy / 2)) ** 2 < 1
    if kind == "polygon":
        path = Path(np.asarray(shape[1], dtype=float))
        pts = np.column_stack([X.ravel(), Y.ravel()])
        return path.contains_points(pts).reshape(X.shape)
    if kind == "rect":
        _, x1, y1, x2, y2 = shape
        return (X > x1) & (X < x2) & (Y > y1) & (Y < y2)
    raise ValueError(f"unknown shape {kind}")


def rasterize(shapes, pixel=PIXEL_NM):
    """Return (mask, x0, y0): mask[iy, ix] covers [x0+ix*p, x0+(ix+1)*p]."""
    boxes = np.array([shape_bbox(s) for s in shapes if s[0] != "subtract"])
    x0 = int(np.floor(boxes[:, 0].min() / pixel) - 1) * pixel
    y0 = int(np.floor(boxes[:, 1].min() / pixel) - 1) * pixel
    nx = int(np.ceil((boxes[:, 2].max() - x0) / pixel)) + 2
    ny = int(np.ceil((boxes[:, 3].max() - y0) / pixel)) + 2
    mask = np.zeros((ny, nx), dtype=bool)
    xc = x0 + (np.arange(nx) + 0.5) * pixel
    yc = y0 + (np.arange(ny) + 0.5) * pixel
    for shape in shapes:
        sub = shape[0] == "subtract"
        geo = shape[1] if sub else shape
        bx1, by1, bx2, by2 = shape_bbox(geo)
        i1 = max(int(np.floor((bx1 - x0) / pixel)) - 1, 0)
        i2 = min(int(np.ceil((bx2 - x0) / pixel)) + 1, nx)
        j1 = max(int(np.floor((by1 - y0) / pixel)) - 1, 0)
        j2 = min(int(np.ceil((by2 - y0) / pixel)) + 1, ny)
        if i2 <= i1 or j2 <= j1:
            continue
        X, Y = np.meshgrid(xc[i1:i2], yc[j1:j2])
        inside = _inside(geo, X, Y)
        if sub:
            mask[j1:j2, i1:i2] &= ~inside
        else:
            mask[j1:j2, i1:i2] |= inside
    return mask, x0, y0


def mask_to_rects(mask, x0, y0, pixel=PIXEL_NM):
    """Column strips merged with identical neighbouring columns -> int nm rects."""
    ny, nx = mask.shape
    rects = []
    open_ = {}  # (ys, ye) -> starting column
    for ix in range(nx + 1):
        col = mask[:, ix] if ix < nx else np.zeros(ny, dtype=bool)
        d = np.diff(np.concatenate(([0], col.astype(np.int8), [0])))
        runs = set(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))
        for run in list(open_):
            if run not in runs:
                ixs = open_.pop(run)
                rects.append((ixs, run[0], ix, run[1]))
        for run in runs:
            if run not in open_:
                open_[run] = ix
    r = np.array(rects, dtype=np.int64).reshape(-1, 4)
    out = np.empty_like(r)
    out[:, 0] = x0 + r[:, 0] * pixel
    out[:, 1] = y0 + r[:, 1] * pixel
    out[:, 2] = x0 + r[:, 2] * pixel
    out[:, 3] = y0 + r[:, 3] * pixel
    return out


def verify_rects(rects, mask, x0, y0, pixel=PIXEL_NM):
    """Paint rects back onto the pixel grid; require exact, non-overlapping cover."""
    paint = np.zeros(mask.shape, dtype=np.int32)
    for x1, y1, x2, y2 in rects:
        paint[(y1 - y0) // pixel:(y2 - y0) // pixel, (x1 - x0) // pixel:(x2 - x0) // pixel] += 1
    if paint.max() > 1:
        raise RuntimeError("overlapping rectangles")
    if not np.array_equal(paint.astype(bool), mask):
        raise RuntimeError("rectangles do not reproduce the raster mask")


def shapes_to_rects(shapes, pixel=PIXEL_NM):
    mask, x0, y0 = rasterize(shapes, pixel)
    rects = mask_to_rects(mask, x0, y0, pixel)
    verify_rects(rects, mask, x0, y0, pixel)
    return rects


# ------------------------------------------------------------------- labels
# seven-segment glyphs on a 0..10 x 0..18 grid (scaled by height / 18); vertical
# segments span the full half height, horizontal ones sit between them, so no two
# segments overlap (no double exposure)
_SEG = {"a": (2, 16, 8, 18), "b": (8, 9, 10, 18), "c": (8, 0, 10, 9),
        "d": (2, 0, 8, 2), "e": (0, 0, 2, 9), "f": (0, 9, 2, 18), "g": (2, 8, 8, 10)}
_DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
           "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
           "-": "g"}


def label_rects(text, x, y, height=10_000):
    """Seven-segment label, lower-left corner at (x, y). Digits and '-' only."""
    s = height / 18
    rects = []
    for k, ch in enumerate(str(text)):
        for seg in _DIGITS[ch]:
            a, b, c, d = _SEG[seg]
            ox = x + k * 14 * s
            rects.append((round(ox + a * s), round(y + b * s), round(ox + c * s), round(y + d * s)))
    return np.array(rects, dtype=np.int64)


def label_width(text, height=10_000):
    return (14 * len(str(text)) - 4) * height / 18


# --------------------------------------------------------------- pat output
def structure(name, rects, repeat=None, increment=INCREMENT, dwell=DWELL_NS):
    """One ECP structure. repeat = (px, py, nx, ny) uses the D-line repetition."""
    head = f"D {name}"
    if repeat is not None:
        head += ", " + ", ".join(str(int(v)) for v in repeat)
    lines = [head, f"I {increment}", f"C {dwell}"]
    lines += [f"RECT {a}, {b}, {c}, {d}" for a, b, c, d in rects]
    lines.append("END")
    return "\n".join(lines) + "\n\n"


def check_field(rects, name):
    if len(rects) == 0:
        raise RuntimeError(f"{name}: empty structure")
    lo, hi = rects[:, :2].min(), rects[:, 2:].max()
    if lo < 0 or hi > FIELD_NM:
        raise RuntimeError(f"{name}: coordinates {lo}..{hi} nm outside 0..{FIELD_NM} nm field")


def translate(shape, dx, dy):
    kind = shape[0]
    if kind == "subtract":
        return ("subtract", translate(shape[1], dx, dy))
    if kind in ("circle", "ellipse"):
        return (kind, shape[1] + dx, shape[2] + dy) + tuple(shape[3:])
    if kind == "polygon":
        return ("polygon", np.asarray(shape[1], dtype=float) + [dx, dy])
    if kind == "rect":
        return ("rect", shape[1] + dx, shape[2] + dy, shape[3] + dx, shape[4] + dy)
    if kind == "compound":
        return ("compound", [translate(s, dx, dy) for s in shape[1]])
    raise ValueError(kind)


def shapes_bbox(shapes):
    b = np.array([shape_bbox(s) for s in shapes if s[0] != "subtract"])
    return b[:, 0].min(), b[:, 1].min(), b[:, 2].max(), b[:, 3].max()


def centre(shapes):
    """Translate a shape list so its bounding box is centred on (0, 0)."""
    x1, y1, x2, y2 = shapes_bbox(shapes)
    return [translate(s, -(x1 + x2) / 2, -(y1 + y2) / 2) for s in shapes]


# ------------------------------------------------------------- chip layout
FIELD_PITCH_UM = 520                  # stage step between write fields of one chip
RESERVED_NM = (0, 0, 80_000, 70_000)  # field 0 corner: numbers_xy.pat labels + direction arrows
LABEL_NM = 8_000                      # device label height
LABEL_GAP_NM = 3_000                  # gap between device and its label


def expand_repeat(rects, repeat):
    """Explicit rects of a structure written with D-line repetition (px, py, nx, ny)."""
    rects = np.asarray(rects, dtype=np.int64)
    if repeat is None:
        return rects
    px, py, nx, ny = repeat
    shifts = np.array([[i * px, j * py, i * px, j * py] for j in range(ny) for i in range(nx)])
    return (rects[None, :, :] + shifts[:, None, :]).reshape(-1, 4)


def _instances(rep):
    px, py, nx, ny = rep if rep else (0, 0, 1, 1)
    return [(i * px, j * py) for j in range(ny) for i in range(nx)]


def _intersections(A, B):
    """Pairwise intersection rectangles (positive area only) of two rect sets."""
    if len(A) == 0 or len(B) == 0:
        return np.zeros((0, 4), dtype=np.int64)
    x1 = np.maximum(A[:, None, 0], B[None, :, 0])
    y1 = np.maximum(A[:, None, 1], B[None, :, 1])
    x2 = np.minimum(A[:, None, 2], B[None, :, 2])
    y2 = np.minimum(A[:, None, 3], B[None, :, 3])
    ok = (x2 > x1) & (y2 > y1)
    return np.column_stack([x1[ok], y1[ok], x2[ok], y2[ok]])


def _subtract(rects, cut):
    """Remove rectangle `cut` from a rect set (each hit rect splits into <= 4 pieces)."""
    cx1, cy1, cx2, cy2 = cut
    hit = (rects[:, 0] < cx2) & (rects[:, 2] > cx1) & (rects[:, 1] < cy2) & (rects[:, 3] > cy1)
    out = [rects[~hit]]
    for x1, y1, x2, y2 in rects[hit]:
        pieces = [(x1, y1, x2, cy1), (x1, cy2, x2, y2),                    # below, above
                  (x1, max(y1, cy1), cx1, min(y2, cy2)), (cx2, max(y1, cy1), x2, min(y2, cy2))]
        out.append(np.array([p for p in pieces if p[2] > p[0] and p[3] > p[1]], dtype=np.int64).reshape(-1, 4))
    return np.concatenate(out)


def make_exposure_unique(structs):
    """Trim structures so that no area is exposed twice (D-line repetition aware).

    structs: list of (name, rects, repeat) in priority order. Each structure loses
    the area it shares with any instance of an earlier structure and with its own
    lower-index copies; the cut is applied to the base rects, i.e. identically to
    all copies, which keeps the repetition valid. Needed because
    generate_pattern.Lattice repeats cells with int(A) while each cell's raster
    spans the exact (non-integer) A, leaving <= 1 nm overlaps per cell boundary.
    """
    done = []
    for name, rects, rep in structs:
        rects = np.asarray(rects, dtype=np.int64)
        own = _instances(rep)
        shifts = set()
        for k2, (ox2, oy2) in enumerate(own):  # own copies: lower index wins
            for ox1, oy1 in own[:k2]:
                shifts.add(("self", ox1 - ox2, oy1 - oy2))
        for e_idx, (_, e_rects, e_rep) in enumerate(done):
            for oxs, oys in own:
                for oxe, oye in _instances(e_rep):
                    shifts.add((e_idx, oxe - oxs, oye - oys))
        base = rects.copy()
        box = (rects[:, 0].min(), rects[:, 1].min(), rects[:, 2].max(), rects[:, 3].max())
        cuts = []
        for src, dx, dy in shifts:
            other = rects if src == "self" else done[src][1]
            ob = (other[:, 0].min() + dx, other[:, 1].min() + dy, other[:, 2].max() + dx, other[:, 3].max() + dy)
            if ob[0] >= box[2] or ob[2] <= box[0] or ob[1] >= box[3] or ob[3] <= box[1]:
                continue
            shifted = other + np.array([dx, dy, dx, dy])
            near = shifted[(shifted[:, 2] > box[0]) & (shifted[:, 0] < box[2])
                           & (shifted[:, 3] > box[1]) & (shifted[:, 1] < box[3])]
            cuts.append(_intersections(base, near))
        for cut in (np.concatenate(cuts) if cuts else []):
            base = _subtract(base, cut)
        done.append((name, base, rep))
    return [(n, r, rep) for n, r, rep in done if len(r)]


def lattice_structures(a1, a2, size_x, size_y, step, shapes_with_args, b_vecs):
    """Lattice via pattern_creator's generate_pattern.Lattice (smallest rectangular
    unit cell found automatically, bulk + 4 edges + 4 corners as in the 2024 KPZ
    lattices), parsed into (suffix, rects, repeat) and made exposure-unique.
    Empty edge/corner structures are dropped. Returns (structures, lattice)."""
    import sys
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if root not in sys.path:
        sys.path.insert(0, root)
    matplotlib.use("Agg")
    from generate_pattern import Lattice
    lat = Lattice(a1, a2, size_x, size_y, step, shapes_with_args, b_vecs, pattern_name="L")
    structs = []
    for block in lat.pat_str.split("END"):
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        head = [v.strip() for v in lines[0][2:].split(",")]
        rep = tuple(int(v) for v in head[1:]) if len(head) == 5 else None
        rects = np.array([[int(v) for v in ln[4:].split(",")] for ln in lines if ln.startswith("RECT")],
                         dtype=np.int64).reshape(-1, 4)
        if len(rects):
            structs.append((head[0][2:], rects, rep))
    # Lattice places the top (y index 1) and right (x index 1) edge/corner cells at
    # n * A (exact) beyond the bulk, but the bulk is repeated with int(A): move them
    # back by n * (A - int(A)) so they abut the last bulk cell (seam <= 1 nm).
    ax, ay = lat.A_x[0], lat.A_y[1]
    dx = -int(round(lat.x_ruc_steps * (ax - int(ax))))
    dy = -int(round(lat.y_ruc_steps * (ay - int(ay))))
    moved = []
    for suffix, rects, rep in structs:
        kx, ky = (int(v) for v in suffix.split("_")[1::2])
        shift = np.array([dx * (kx == 1), dy * (ky == 1)] * 2)
        moved.append((suffix, rects + shift, rep))
    order = sorted(moved, key=lambda s: (s[0] != "x_0_y_0", s[0].count("_0") == 0))
    return make_exposure_unique(order), lat


def dev_bbox(dev):
    """Bounding box of a device given by 'shapes' or by pre-made 'structures'.

    structures: list of (suffix, rects (int nm, local coords), repeat or None).
    """
    if "structures" in dev:
        r = np.concatenate([expand_repeat(rects, rep) for _, rects, rep in dev["structures"]])
        return r[:, 0].min(), r[:, 1].min(), r[:, 2].max(), r[:, 3].max()
    return shapes_bbox(dev["shapes"])


def pack_compact(groups, margin=10_000, step=5_000, **kw):
    """Single-field packing with the lowest possible top edge (content sits low).

    Returns (fields, chip_height_nm). Falls back to multi-field packing when
    the devices do not fit into one field.
    """
    for top in range(RESERVED_NM[3], FIELD_NM - margin + 1, step):
        try:
            return pack_chip(groups, margin=margin, top=top, max_fields=1, **kw), top + margin
        except OverflowError:
            continue
    return pack_chip(groups, margin=margin, **kw), FIELD_NM


def pack_chip(groups, margin=10_000, gap_x=15_000, gap_y=10_000, top=None, max_fields=None):
    """Pack devices into 500 um write fields, rows top to bottom, left to right.

    groups: list of (system, devices); device = dict(name, shapes, params).
    Every system starts on a new row. Devices are numbered 1, 2, ... in chip
    order; that number is written below each device. Returns a list of fields,
    each a list of placed devices (keys pos, label, label_pos, system added).
    top: y of the first row in field 0 (default: top of the field).
    max_fields: raise OverflowError instead of opening more fields.
    """
    fields = [[]]
    state = {"x": margin, "y": (FIELD_NM - margin) if top is None else top, "row_h": 0}

    def new_row():
        state["x"] = margin
        state["y"] -= state["row_h"] + gap_y
        state["row_h"] = 0

    number = 1
    for system, devs in groups:
        if state["x"] > margin:
            new_row()
        for dev in devs:
            label = str(number)
            bx1, by1, bx2, by2 = dev_bbox(dev)
            w = max(bx2 - bx1, label_width(label, LABEL_NM))
            h = by2 - by1 + LABEL_GAP_NM + LABEL_NM
            if w > FIELD_NM - 2 * margin or h > FIELD_NM - 2 * margin:
                raise RuntimeError(f"{system}/{dev['name']} does not fit into one write field")
            while True:  # each pass moves right, down or to a new field; terminates
                if state["x"] + w > FIELD_NM - margin and state["x"] > margin:
                    new_row()
                if (len(fields) == 1 and state["y"] - h < RESERVED_NM[3]
                        and state["x"] < RESERVED_NM[2] + gap_x):
                    state["x"] = RESERVED_NM[2] + gap_x
                    continue
                if state["y"] - h < margin:
                    if max_fields is not None and len(fields) >= max_fields:
                        raise OverflowError("devices do not fit")
                    fields.append([])
                    state.update(x=margin, y=FIELD_NM - margin, row_h=0)
                    continue
                break
            x, y = state["x"], state["y"]
            fields[-1].append(dict(dev, system=system, label=label,
                                   pos=(int(round(x - bx1)), int(round(y - by2))),
                                   label_pos=(x, y - (by2 - by1) - LABEL_GAP_NM - LABEL_NM)))
            state["x"] += w + gap_x
            state["row_h"] = max(state["row_h"], h)
            number += 1
    return fields


def safe_name(text):
    """ECP structure names allow letters, digits, '-' and '_'; '.' becomes 'p'."""
    return "".join(c if (c.isalnum() or c in "_-") else "p" if c == "." else "_" for c in str(text))


def write_chip(out_dir, chip, fields, header, current_pA=25000, numbers_box=RESERVED_NM, write_ctl=True):
    """Rasterise a packed chip; write <chip>.pat, device CSV, previews and (optionally) <chip>.ctl.

    Coordinates in the pat file are absolute within each 500 um write field.
    The ctl moves the stage by FIELD_PITCH_UM per field (relative to the chip
    origin) and draws every structure of that field. With write_ctl=False the
    caller writes its own ctl (e.g. grid_ctl) from the returned structure names.
    """
    os.makedirs(out_dir, exist_ok=True)
    pat = [f"; {line}\n" for line in header] + ["\n"]
    ctl = [f"; {line}\n" for line in header]
    ctl += ["\n", f"current = {current_pA}\n", "origin = 0, 0\n", "\n", f"sfile = {chip}\n"]
    rows, overview, field_names = [], [], []
    for k, devs in enumerate(fields):
        groups, lab_all, names = [], [], []
        for dev in devs:
            base = safe_name(f"{chip}_f{k}_{dev['system']}_{dev['name']}")
            dx, dy = dev["pos"]
            if "structures" in dev:
                parts = [(f"{base}_{sfx}" if sfx else base,
                          np.asarray(r, dtype=np.int64) + np.array([dx, dy, dx, dy]), rep)
                         for sfx, r, rep in dev["structures"]]
            else:
                shapes = [translate(s, dx, dy) for s in dev["shapes"]]
                parts = [(base, shapes_to_rects(shapes, dev.get("pixel", PIXEL_NM)), None)]
            expanded = []
            for name, rects, rep in parts:
                full = expand_repeat(rects, rep)
                check_field(full, name)
                pat.append(structure(name, rects, repeat=rep))
                names.append(name)
                expanded.append(full)
            expanded = np.concatenate(expanded)
            groups.append((expanded, "k"))
            if dev.get("label"):  # fixed markers (e.g. arrows) carry no device number
                lab_all.append(label_rects(dev["label"], *dev["label_pos"], LABEL_NM))
            x1, y1 = expanded[:, :2].min(0)
            x2, y2 = expanded[:, 2:].max(0)
            rows.append({"chip": chip, "label": dev.get("label") or "", "field": k, "system": dev["system"],
                         "structure": base, "n_structures": len(parts), "x_centre_um": (x1 + x2) / 2e3,
                         "y_centre_um": (y1 + y2) / 2e3, "width_um": (x2 - x1) / 1e3,
                         "height_um": (y2 - y1) / 1e3, "n_rects_written": sum(len(p[1]) for p in parts),
                         "raster_nm": dev.get("pixel", PIXEL_NM),
                         **{f"{m}_{ax}_um": round((xy[i] + dev["pos"][i]) / 1e3, 3)
                            for m, xy in dev.get("marks", {}).items() for i, ax in enumerate("xy")},
                         **dev.get("params", {})})
        lab_all = np.concatenate(lab_all)
        lab_name = f"{chip}_f{k}_labels"
        check_field(lab_all, lab_name)
        pat.append(structure(lab_name, lab_all))
        names.append(lab_name)
        field_names.append(names)
        groups.append((lab_all, "tab:red"))
        frame = np.array([[0, 0, FIELD_NM, 800], [0, FIELD_NM - 800, FIELD_NM, FIELD_NM],
                          [0, 0, 800, FIELD_NM], [FIELD_NM - 800, 0, FIELD_NM, FIELD_NM]])
        if k == 0:
            r = numbers_box
            groups.append((np.array([[r[0], r[1], r[2], r[3]]]), "#cfe3ff"))
        preview(os.path.join(out_dir, f"{chip}_f{k}_preview.png"), groups + [(frame, "0.8")],
                title=f"{chip}, write field {k} (grey frame = 500 um field, blue = chip numbers)")
        shift = np.array([k * FIELD_PITCH_UM * 1000, 0, k * FIELD_PITCH_UM * 1000, 0])
        overview += [(g[0] + shift, g[1]) for g in groups] + [(frame + shift, "0.8")]
        ctl += ["\n", f"; ===== write field {k}\n", f"x = {k * FIELD_PITCH_UM}\n", "y = 0\n", "stage\n"]
        ctl += [f"draw({n})\n" for n in names]
    ctl += ["\n", "END\n"]
    with open(os.path.join(out_dir, f"{chip}.pat"), "w") as f:
        f.write("".join(pat))
    if write_ctl:
        with open(os.path.join(out_dir, f"{chip}.ctl"), "w") as f:
            f.write("".join(ctl))
    keys = []
    for r in rows:
        keys += [k_ for k_ in r if k_ not in keys]
    with open(os.path.join(out_dir, f"{chip}_devices.csv"), "w") as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(str(r.get(k_, "")) for k_ in keys) + "\n")
    preview(os.path.join(out_dir, f"{chip}_overview.png"), overview, title=f"{chip} overview")
    width_um = (len(fields) - 1) * FIELD_PITCH_UM + FIELD_NM / 1000
    return {"chip": chip, "n_fields": len(fields), "width_um": width_um, "height_um": FIELD_NM / 1000,
            "devices": rows, "structures": field_names}



def grid_ctl(path, chip, structure_names, nx, ny, pitch_x, pitch_y, header=(), numbers_file="numbers_xy"):
    """Exposure ctl: the chip field nx x ny times, each with its x/y index labels.

    At every grid position: one stage move, all chip structures (sfile = chip),
    then the labels nbr_x_<n> / nbr_y_<m> from numbers_file (2024 numbers_xy.pat
    glyphs, labels 0..98). Large nx, ny make ECP slow to display; check small first.
    """
    if nx > 98 or ny > 98:
        raise ValueError("numbers_xy.pat only contains labels 0..98")
    with open(path, "w") as f:
        f.write("".join(f"; {line}\n" for line in header)
                + f"; grid {nx} x {ny} fields, pitch {pitch_x} x {pitch_y} um, field x/y index labels from "
                  f"{numbers_file}.pat\n\n"
                "current = 25000\n\norigin = 0, 0\nx = 0\ny = 0\nstage\n\n"
                f"for m = 1 to {ny}\nx = 0\nfor n = 1 to {nx}\nstage\n\n"
                f"sfile = {chip}\n" + "".join(f"draw({s})\n" for s in structure_names)
                + f"\nsfile = {numbers_file}\nidraw(nbr_x_, n)\nidraw(nbr_y_, m)\n\n"
                f"+x = {pitch_x}\nnext n\n+y = {pitch_y}\nnext m\n\nEND\n")


def dose_ranks(dwells_ns, current_pA, increment, unit_nm=1.0):
    """ECP's JEOL export rule (reproduces the 2024 HC_TOPO and KPZ jobs exactly): every
    distinct dwell time becomes a shot rank, ascending; rank 0 = shortest dwell.
    RESIST = current * dwell_min / (increment * unit)^2 in uC/cm^2 (truncated),
    MODULAT % = (dwell / dwell_min - 1) * 100 (truncated)."""
    d = sorted(set(float(v) for v in dwells_ns))
    step_cm = increment * unit_nm * 1e-7
    resist = int(current_pA * 1e-12 * d[0] * 1e-9 / step_cm ** 2 * 1e6)
    return resist, [(k, int((v / d[0] - 1) * 100 + 1e-9)) for k, v in enumerate(d)], d


def pat_dwells(*paths):
    """All dwell times (C lines) and increments (I lines) used in pat files."""
    dwells, incs = set(), set()
    for p in paths:
        for line in open(p):
            if line.startswith("C "):
                dwells.add(float(line[2:]))
            elif line.startswith("I "):
                incs.add(int(line[2:]))
    return dwells, incs


def job_jdf(path, v30_name, dwells_ns, current_pA=25000, increment=16):
    """Job file placing one .v30 once (the grid ctl already contains all fields).

    RESIST and the MODULAT shot-rank table follow ECP's JEOL export rule
    (dose_ranks) for the dwell times used in the pat files. SHOT / STDCUR /
    CALPRM are copied from the 2024 EnO jobs and must be checked at the tool.
    ECP's own export may write a jdf too: compare, they must agree.
    Also writes the matching .sdf.
    """
    resist, ranks, d = dose_ranks(dwells_ns, current_pA, increment)
    modulat = ", ".join(f"({k}, {m})" for k, m in ranks)
    with open(path, "w") as f:
        f.write(f"\nJOB 'EBL', 2 \n\n; Etch and overgrow 2026: {v30_name}.v30 (exported by ECP, File -> Export -> JEOL)\n"
                f"; shot ranks = dwell times {', '.join(f'{v:g}' for v in d)} ns at {current_pA} pA, I {increment}\n\n"
                "PATH MINI \n"
                "  ARRAY (0, 1, 0) / (0, 1, 0) \n    ASSIGN P(1) -> ( (*,*), SHOT01) \n  AEND \n"
                "PEND \n\nLAYER 1 \n\n"
                f"P(1) '{v30_name}.v30' (0, 0)\n\n"
                f"SHOT01: MODULAT ({modulat}) \n\n"
                f"SHOT A, 4 \n\nRESIST {resist}\n\nSTDCUR 2 \n\nEND \n")
    name = os.path.splitext(os.path.basename(path))[0]
    with open(path[:-4] + ".sdf", "w") as f:
        f.write(f"\nMAGAZIN 'TEP' \n\nMTRL STKR \n\n#5 \n%4A \n\nJDF '{name}', 1\nACC 100 \n"
                "CALPRM 'TEP_60um_2nA' \nDEFMODE 2 \nOFFSET (0, 0) \n\nEND 5 \n")


def preview(path, groups, title="", xlim=None, ylim=None, dpi=200):
    """groups: list of (rects, colour). Writes a PNG preview in um."""
    matplotlib.use("Agg")
    fig, ax = plt.subplots(figsize=(10, 10))
    for rects, colour in groups:
        r = np.asarray(rects, dtype=float) / 1000
        polys = np.stack([r[:, [0, 1]], r[:, [2, 1]], r[:, [2, 3]], r[:, [0, 3]]], axis=1)
        ax.add_collection(PolyCollection(polys, facecolors=colour, edgecolors="none"))
    ax.autoscale()
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.set_xlabel("x (um)")
    ax.set_ylabel("y (um)")
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)





