"""Compare an ECP-exported .v30 with the .ctl/.pat it was exported from, rectangle by rectangle.

Expected geometry: for every grid position of the grid ctl, all field structures
(D-line repetition expanded) plus the two number glyphs (P 0 = RECT), shifted by the
stage position. Actual geometry: all rectangles of the .v30 (command omission and
compaction mode 8 expanded), field position + position-set + rect, converted from
JEOL chip coordinates (y down) to ECP coordinates (y up) with one global transform
found from the data. Reports per field: rect counts, exact multiset match, shot ranks.

usage: python compare_v30.py <file.v30> <grid.ctl>
"""
import os
import re
import sys
from collections import Counter

import numpy as np

from check_pat import read_pat
from read_v30 import GEOM, b4, read_id, records, scan_commands


def v30_fields(path):
    """Yield per text block: field position, list of (x1, y1, x2, y2, rank) in chip coords (y down)."""
    recs, _ = records(path)
    fields, cur = [], None
    rank, pos, comp = 0, (0, 0), None
    for r in recs[1:]:
        for ev in scan_commands(r):
            kind = ev[0]
            if kind == "field":
                cur = {"field": ev[1], "rects": []}
                fields.append(cur)
                rank, comp = 0, None
            elif kind == "shot_rank":
                rank = ev[1]
            elif kind == "position_set":
                pos, comp = ev[1], None
            elif kind == "compaction8":
                npt, lx, ly, nx, ny = ev[1]
                comp = {"left": npt, "lx": lx, "ly": ly, "nx": nx, "ny": ny}
            elif kind.endswith("rect"):
                d = ev[1]
                if kind.startswith(("XLL", "YLL")):
                    x1, y1, w, h = b4(d, 0), b4(d, 2), b4(d, 4), b4(d, 6)
                else:
                    x1, y1, w, h = (int(v) for v in d[:4])
                fx, fy = cur["field"]
                base = (fx + pos[0] + x1, fy + pos[1] + y1)
                reps = [(0, 0)]
                if comp is not None and comp["left"] > 0:
                    # Lx, Ly = distance from the first to the last repetition (verified against
                    # ECP exports: Lx = (Nx - 1) * pitch), not the pitch itself
                    px = comp["lx"] // (comp["nx"] - 1) if comp["nx"] > 1 else 0
                    py = comp["ly"] // (comp["ny"] - 1) if comp["ny"] > 1 else 0
                    if (comp["nx"] > 1 and px * (comp["nx"] - 1) != comp["lx"]) or \
                       (comp["ny"] > 1 and py * (comp["ny"] - 1) != comp["ly"]):
                        raise RuntimeError(f"non-integer compaction pitch {comp}")
                    reps = [(i * px, j * py) for j in range(comp["ny"]) for i in range(comp["nx"])]
                    comp["left"] -= 1
                    if comp["left"] == 0:
                        comp = None
                for dx, dy in reps:
                    cur["rects"].append((base[0] + dx, base[1] + dy, base[0] + dx + w, base[1] + dy + h, rank))
            elif kind.endswith("trap"):
                raise RuntimeError("trapezoids not expected in this layout")
    return fields


def expected_fields(ctl_path):
    d = os.path.dirname(ctl_path)
    ctl = open(ctl_path).read()
    sfiles = re.findall(r"^sfile = (\S+)", ctl, flags=re.M)
    draws = re.findall(r"^draw\((\S+)\)", ctl, flags=re.M)
    nx = int(re.search(r"for n = 1 to (\d+)", ctl).group(1))
    ny = int(re.search(r"for m = 1 to (\d+)", ctl).group(1))
    px = int(re.search(r"\+x = (\d+)", ctl).group(1)) * 1000
    py = int(re.search(r"\+y = (\d+)", ctl).group(1)) * 1000
    field = read_pat(os.path.join(d, sfiles[0] + ".pat"))
    numtxt = open(os.path.join(d, sfiles[1] + ".pat")).read()
    numtxt = "\n".join("RECT" + ln[4:] if ln.startswith("P 0,") else ln for ln in numtxt.splitlines())
    tmp = os.path.join(d, "_numbers_rect.tmp.pat")
    open(tmp, "w").write(numtxt)
    nums = read_pat(tmp)
    os.unlink(tmp)
    dwell = {}
    for name, pat_file in [(n, sfiles[0]) for n in draws]:
        dwell[name] = None
    base = np.concatenate([field[n] for n in draws])
    out = []
    for m in range(1, ny + 1):
        for n in range(1, nx + 1):
            off = np.array([(n - 1) * px, (m - 1) * py] * 2)
            r = np.concatenate([base, nums[f"nbr_x_{n}"], nums[f"nbr_y_{m}"]]) + off
            out.append(((n, m), r))
    return out


if __name__ == "__main__":
    v30, ctl = sys.argv[1], sys.argv[2]
    head = read_id(records(v30)[0][0])
    fields = v30_fields(v30)
    exp = expected_fields(ctl)
    print(f"v30: {len(fields)} text blocks, ID says {head['n_textblocks']}; decompacted rects "
          f"{sum(len(f['rects']) for f in fields)} (ID record: {head['n_rect_decompacted_L']})")
    chip_y = head["chip_size"][1]
    # JEOL y axis points down: convert to y-up and find the global offset from the first field
    act = []
    for f in fields:
        a = np.array(f["rects"], dtype=np.int64)
        y1 = chip_y - a[:, 3]
        y2 = chip_y - a[:, 1]
        act.append(np.column_stack([a[:, 0], y1, a[:, 2], y2, a[:, 4]]))
    # match fields by bounding-box order (both lists sorted by lower-left corner)
    act.sort(key=lambda a: (a[:, 1].min(), a[:, 0].min()))
    exp.sort(key=lambda e: (e[1][:, 1].min(), e[1][:, 0].min()))
    shift = act[0][:, :2].min(0) - exp[0][1][:, :2].min(0)
    print(f"global offset v30 -> ctl coordinates: {shift} nm (chip size {head['chip_size']})")
    all_ok = True
    for a, (nm, e) in zip(act, exp):
        a_r = a[:, :4] - np.array([*shift, *shift])
        ca = Counter(map(tuple, a_r.tolist()))
        ce = Counter(map(tuple, e.tolist()))
        missing = sum((ce - ca).values())
        extra = sum((ca - ce).values())
        ranks = Counter(a[:, 4].tolist())
        ok = missing == 0 and extra == 0
        all_ok &= ok
        print(f"field (x={nm[0]}, y={nm[1]}): v30 rects {len(a_r)}, expected {len(e)}, "
              f"missing {missing}, extra {extra}, shot ranks {dict(ranks)} -> {'IDENTICAL' if ok else 'DIFFERENT'}")
    print("RESULT:", "v30 geometry identical to ctl/pat" if all_ok else "differences found")
