"""Verify the Semenoff domain-wall field against its explicit disk list (semenoff_walls.py -> semw_sites.npz).

Per lattice, a window of WIN_UM x WIN_UM around the middle of the wall is painted on a 5 nm grid from the written
pat (exact rects) and compared with the analytic union of the disks: area XOR / disk area, and per pillar class
(large/small x wall/bulk) the exposed area inside each pillar's power-diagram cell vs the analytic disk-in-cell
area, as an equivalent-diameter error. Field index labels: exact test of the field rects against the bounding box
of numbers_semw.pat. Files: ctl/pat/jdf consistency as verify_semenoff.check_files.

usage: python verify_semenoff_walls.py <layout_dir>
"""
import csv
import os
import re
import sys

import numpy as np

from check_pat import read_pat, read_pat_raw

PIX = 5
WIN_UM = 14.0


def main(layout):
    pat = read_pat(os.path.join(layout, "semw_field.pat"))
    sites_all = np.load(os.path.join(layout, "semw_sites.npz"))
    rows = list(csv.DictReader(open(os.path.join(layout, "semw_field_devices.csv"))))
    print("== geometry vs explicit disk list")
    worst = 0.0
    for row in rows:
        if "_dw_" not in row["structure"]:
            continue
        name = row["structure"].split("_dw_")[1]
        S = sites_all[name]                                  # x, y, d, big, lab, above (nm, field coords)
        rects = pat[row["structure"]]
        yw = float(row["wall_left_y_um"]) * 1000
        xc = float(row["x_centre_um"]) * 1000
        x0, y0 = int(xc - WIN_UM * 500), int(yw - WIN_UM * 500)
        n = int(WIN_UM * 1000 / PIX)
        m = np.zeros((n, n), bool)
        sel = (rects[:, 2] > x0) & (rects[:, 0] < x0 + n * PIX) & (rects[:, 3] > y0) & (rects[:, 1] < y0 + n * PIX)
        for a, b, c, d in rects[sel]:
            m[max((b - y0) // PIX, 0):min((d - y0) // PIX, n), max((a - x0) // PIX, 0):min((c - x0) // PIX, n)] = True
        xs = x0 + (np.arange(n) + 0.5) * PIX
        ys = y0 + (np.arange(n) + 0.5) * PIX
        X, Y = np.meshgrid(xs, ys)
        near = (np.abs(S[:, 0] - xc) < WIN_UM * 500 + 3000) & (np.abs(S[:, 1] - yw) < WIN_UM * 500 + 3000)
        Sn = S[near]
        ref = np.zeros((n, n), bool)
        pw = np.full((n, n), np.inf)
        owner = np.full((n, n), -1)
        for i, (sx, sy, d, *_r) in enumerate(Sn):
            d2 = (X - sx) ** 2 + (Y - sy) ** 2
            ref |= d2 < (d / 2) ** 2
            p = d2 - (d / 2) ** 2
            better = p < pw
            pw[better], owner[better] = p[better], i
        mism = np.sum(m ^ ref) / max(np.sum(ref), 1)
        inner = (np.abs(Sn[:, 0] - xc) < WIN_UM * 500 - 2500) & (np.abs(Sn[:, 1] - yw) < WIN_UM * 500 - 2500)
        cls = {}
        for i in np.flatnonzero(inner):
            got, want = np.sum(m & (owner == i)), np.sum(ref & (owner == i))
            dD = 2 * (got - want) * PIX * PIX / (2 * np.pi * Sn[i, 2] / 2)
            wall = abs(Sn[i, 1] - yw) < 0.6 * float(row["a_nn_nm"])
            key = ("large" if Sn[i, 3] else "small") + ("/wall" if wall else "/bulk")
            cls.setdefault(key, []).append(dD)
        txt = " | ".join(f"{k}: {np.mean(v):+5.1f} nm (max {np.max(np.abs(v)):4.1f}, n {len(v)})" for k, v in sorted(cls.items()))
        worst = max([worst] + [np.max(np.abs(v)) for v in cls.values()])
        print(f"  {row['label']:>2} {name:<16} XOR {100 * mism:5.2f} % | {txt}")
    print(f"  worst per-pillar equivalent-diameter error: {worst:.1f} nm")
    # field index labels: exact bounding-box test (check_with_numbers.py is O(n^2) on the explicit disks)
    # the glyphs use the numeric shape code 'P 0, x1, y1, x2, y2' (= RECT, see check_with_numbers.py)
    nb = np.array([[int(float(v)) for v in ln[4:].split(",")[:4]]
                   for ln in open(os.path.join(layout, "numbers_semw.pat")) if ln.startswith("P 0,")])
    bx = (nb[:, 0].min(), nb[:, 1].min(), nb[:, 2].max(), nb[:, 3].max())
    hit = [s for s, r in pat.items() if np.any((r[:, 2] > bx[0]) & (r[:, 0] < bx[2]) & (r[:, 3] > bx[1]) & (r[:, 1] < bx[3]))]
    print(f"== numbers_semw.pat bounding box {tuple(int(v) for v in bx)} nm; field structures overlapping it: "
          f"{hit if hit else 'none -> no double exposure with any field index label'}")
    print("== file consistency (semw_grid.ctl, semw_field.pat, numbers_semw.pat, semw_grid.jdf)")
    raw = read_pat_raw(os.path.join(layout, "semw_field.pat"))
    names = re.findall(r"^D (\S+?)(?:,|$)", open(os.path.join(layout, "semw_field.pat")).read(), flags=re.M)
    text = open(os.path.join(layout, "semw_grid.ctl")).read()
    draws = re.findall(r"^draw\((\S+)\)", text, flags=re.M)
    print(f"  semw_grid.ctl: {len(draws)} draws per field, not drawn {sorted(set(names) - set(draws))}, unknown draws "
          f"{sorted(set(draws) - set(names))}, ends with END {text.strip().upper().endswith('END')}, empty structures "
          f"{[x for x in names if x not in raw]}")
    print(f"  semw_grid.jdf places: {re.findall(r'P\(\d\) .(\S+?).\s', open(os.path.join(layout, 'semw_grid.jdf')).read())}")


if __name__ == "__main__":
    main(sys.argv[1])
