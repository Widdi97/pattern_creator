"""Verify the vortex-waveguide ECP files against the GPE geometry and against each other.

1. Geometry: every guide in vwg_field_devices.csv must be written as exactly one rectangle of
   width_nm x length_nm (x across, y along the guide, as model_definitions._rectangular_waveguide_mask),
   at the CSV centre, and neighbouring guides must be separated by etched barrier (no contact).
2. Files: vwg_grid.ctl draws every structure of the pat once per field (and nothing else), all number
   structures needed by its loops exist, it ends with END, and the jdf places vwg_grid.v30.

usage: python verify_waveguides.py <layout_dir>
"""
import csv
import os
import re
import sys

import numpy as np

from check_pat import read_pat, read_pat_raw


def check_geometry(pat, rows):
    print("== geometry vs GPE waveguide (one rect W x L per guide)")
    bad, boxes = 0, []
    for row in rows:
        if row["system"] != "wg":
            continue
        rects = pat[row["structure"]]
        W, L = int(row["width_nm"]), int(row["length_nm"])
        ok = len(rects) == 1
        if ok:
            x1, y1, x2, y2 = rects[0]
            ok = (x2 - x1 == W) and (y2 - y1 == L)
            cx, cy = (x1 + x2) / 2e3, (y1 + y2) / 2e3
            ok &= abs(cx - float(row["x_centre_um"])) < 1e-6 and abs(cy - float(row["y_centre_um"])) < 1e-6
            boxes.append((x1, y1, x2, y2))
        if not ok:
            bad += 1
            print(f"  MISMATCH {row['label']:>3} {row['structure']}: {rects.tolist()}")
    b = np.array(boxes)
    gaps = []
    for i in range(len(b)):
        same_row = (b[:, 1] < b[i, 3]) & (b[:, 3] > b[i, 1])
        right = b[same_row & (b[:, 0] >= b[i, 2])]
        if len(right):
            gaps.append(right[:, 0].min() - b[i, 2])
    print(f"  {len(boxes)} guides, {bad} mismatches; widths {sorted(set((b[:, 2] - b[:, 0]).tolist()))} nm, "
          f"lengths {sorted(set((b[:, 3] - b[:, 1]).tolist()))} nm; smallest etched gap to the right neighbour "
          f"{min(gaps) / 1e3:.3f} um")
    return bad


def check_files(layout_dir):
    print("== file consistency (vwg_grid.ctl, vwg_field.pat, numbers pat, vwg_grid.jdf)")
    raw = read_pat_raw(os.path.join(layout_dir, "vwg_field.pat"))
    with open(os.path.join(layout_dir, "vwg_field.pat")) as f:
        all_names = re.findall(r"^D (\S+?)(?:,|$)", f.read(), flags=re.M)
    text = open(os.path.join(layout_dir, "vwg_grid.ctl")).read()
    draws = re.findall(r"^draw\((\S+)\)", text, flags=re.M)
    print(f"  vwg_grid.ctl: {len(draws)} draws per field, pat structures not drawn "
          f"{sorted(set(all_names) - set(draws))}, draws not in pat {sorted(set(draws) - set(all_names))}, "
          f"duplicate draws {len(draws) - len(set(draws))}, ends with END {text.strip().upper().endswith('END')}")
    print(f"  empty structures in pat: {[n for n in all_names if n not in raw]}")
    ny = int(re.search(r"for m = 1 to (\d+)", text).group(1))
    nx = int(re.search(r"for n = 1 to (\d+)", text).group(1))
    px = int(re.search(r"\+x = (\d+)", text).group(1))
    py = int(re.search(r"\+y = (\d+)", text).group(1))
    sfiles = re.findall(r"^sfile = (\S+)", text, flags=re.M)
    nums = open(os.path.join(layout_dir, sfiles[-1] + ".pat")).read()
    have = set(re.findall(r"^D (nbr_[xy]_\d+)", nums, flags=re.M))
    need = {f"nbr_x_{i}" for i in range(1, nx + 1)} | {f"nbr_y_{i}" for i in range(1, ny + 1)}
    print(f"  grid {nx} x {ny} at {px} x {py} um; sfiles {sfiles}; number structures needed {len(need)}, "
          f"missing {sorted(need - have)}")
    jdf = open(os.path.join(layout_dir, "vwg_grid.jdf")).read()
    print(f"  vwg_grid.jdf places: {re.findall(r'P\(\d\) .(\S+?).\s', jdf)}")


if __name__ == "__main__":
    layout = sys.argv[1]
    with open(os.path.join(layout, "vwg_field_devices.csv")) as f:
        rows = list(csv.DictReader(f))
    n_bad = check_geometry(read_pat(os.path.join(layout, "vwg_field.pat")), rows)
    check_files(layout)
    sys.exit(1 if n_bad else 0)
