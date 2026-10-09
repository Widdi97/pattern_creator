"""Verify the stretched-honeycomb ECP files against the GPE geometry and against each other.

1. Geometry: for every lattice in shc_field_devices.csv the expected pillar centres
   are rebuilt with the formulas of
   tep_polariton_gpe_code/.../adiabatic_topology_blueshift/gpe_v3_optimise.py:54-64
       a = 2 r v, a_latt = 3 a, a1 = a_latt (1, 0), a2 = a_latt (cos 60, sin 60),
       b_k = (a + s)(cos 60k, sin 60k), circle radius r
   and compared with the pillars found in shc_field.pat (D-line repetition expanded):
   centre positions (after one global translation), equivalent diameters, and the
   intra-/inter-hexamer centre distances.
2. Files: shc_grid.ctl draws every structure of the pat once per field (and nothing
   else), all number structures needed by its loops exist, it ends with END, and the
   jdf places shc_grid.v30.

usage: python verify_layout.py <layout_dir>
"""
import csv
import os
import re
import sys

import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

from check_pat import read_pat, read_pat_raw

PIX = 5  # nm, painting step for the pillar analysis (pattern coordinates are integer nm)


def components(rects):
    """Connected pillars of a rect set: exact area-weighted centroids and areas."""
    x0, y0 = rects[:, 0].min(), rects[:, 1].min()
    nx = (rects[:, 2].max() - x0) // PIX + 2
    ny = (rects[:, 3].max() - y0) // PIX + 2
    m = np.zeros((ny, nx), dtype=bool)
    for a, b, c, d in rects:  # dilate by one pixel so <= 1 nm seams between Lattice parts do not split pillars
        m[max((b - y0) // PIX - 1, 0):(d - y0) // PIX + 1, max((a - x0) // PIX - 1, 0):(c - x0) // PIX + 1] = True
    lab, n = ndimage.label(m)
    cy = ((rects[:, 1] + rects[:, 3]) / 2 - y0) // PIX
    cx = ((rects[:, 0] + rects[:, 2]) / 2 - x0) // PIX
    comp = lab[cy.astype(int), cx.astype(int)]
    area = ((rects[:, 2] - rects[:, 0]) * (rects[:, 3] - rects[:, 1])).astype(float)
    A = np.bincount(comp, area, n + 1)[1:]
    X = np.bincount(comp, area * (rects[:, 0] + rects[:, 2]) / 2, n + 1)[1:] / A
    Y = np.bincount(comp, area * (rects[:, 1] + rects[:, 3]) / 2, n + 1)[1:] / A
    return np.column_stack([X, Y]), A


def gpe_sites(r, v, s, n_range=60):
    """Pillar centres exactly as gpe_v3_optimise.py builds them (nm)."""
    a = 2 * r * v
    a_latt = 3 * a
    a1 = a_latt * np.array([1.0, 0.0])
    a2 = a_latt * np.array([np.cos(np.deg2rad(60)), np.sin(np.deg2rad(60))])
    bs = np.array([(a + s) * np.array([np.cos(np.deg2rad(60 * k)), np.sin(np.deg2rad(60 * k))]) for k in range(6)])
    n = np.arange(-n_range, n_range + 1)
    N, M = np.meshgrid(n, n, indexing="ij")
    pts = (N.ravel()[:, None] * a1 + M.ravel()[:, None] * a2)
    return (pts[:, None, :] + bs[None]).reshape(-1, 2), a, a_latt


def check_geometry(layout_dir, pat, rows):
    print("== geometry vs gpe_v3_optimise.py construction")
    worst = 0.0
    for row in rows:
        if not row["structure"].startswith("shc_field_f0_kek_"):
            continue
        d, v, s = float(row["d_nm"]), float(row["v_a_over_d"]), float(row["s_nm"])
        r = d / 2
        rects = np.concatenate([rr for name, rr in pat.items() if name.startswith(row["structure"] + "_x_")])
        cen, area = components(rects)
        sites, a, a_latt = gpe_sites(r, v, s)
        inter_gap = a - 2 * s - d
        if inter_gap <= 0:  # merged dimers: compare dimer centres and the total exposed area instead
            exp_area_pillar = np.pi * r ** 2
            print(f"  {row['label']:>2} {row['structure'][17:]:<14} gap {inter_gap:7.1f} nm -> {len(cen)} merged dimers, "
                  f"area per dimer / (2 pi r^2) = {np.median(area) / (2 * exp_area_pillar):.4f} (overlap lens removed)")
            continue
        # global translation: align the measured pillar nearest to the lattice centre with the GPE sites
        mid = cen.mean(0)
        c0 = cen[np.argmin(np.linalg.norm(cen - mid, axis=1))]
        tree_meas = cKDTree(cen)
        best = None
        for site in sites[np.linalg.norm(sites, axis=1) < 3 * a_latt]:
            t = c0 - site
            dist, _ = cKDTree(sites + t).query(cen)
            score = np.sum(dist < 30)
            if best is None or score > best[0]:
                best = (score, t)
        dist, idx = cKDTree(sites + best[1]).query(cen)
        t = best[1] + np.mean(cen - (sites[idx] + best[1]), axis=0)  # refine with the mean residual
        dist, idx = cKDTree(sites + t).query(cen)
        d_eq = 2 * np.sqrt(area / np.pi)
        nn, _ = tree_meas.query(cen, k=4)
        inter_meas = nn[:, 1][nn[:, 1] < (a - 2 * s + a + s) / 2]
        intra_cand = nn[:, 1:][(nn[:, 1:] > (a - 2 * s + a + s) / 2) & (nn[:, 1:] < a + s + 0.3 * a)]
        print(f"  {row['label']:>2} {row['structure'][17:]:<14} pillars {len(cen):4d}, matched {np.sum(dist < 30):4d}, "
              f"centre error rms {np.sqrt(np.mean(dist ** 2)):4.1f} / max {dist.max():4.1f} nm | "
              f"d_eq {np.median(d_eq):7.1f} (target {d:.1f}) | "
              f"inter cc {np.median(inter_meas):7.1f} (GPE {a - 2 * s:7.1f}) | "
              f"intra cc {np.median(intra_cand):7.1f} (GPE {a + s:7.1f})")
        worst = max(worst, dist.max())
        if np.sum(dist < 30) != len(cen):
            print("     WARNING: pillars that do not sit on GPE lattice sites")
    print(f"  worst centre deviation over all separated-pillar lattices: {worst:.1f} nm")


def check_files(layout_dir):
    print("== file consistency (shc_grid.ctl, shc_field.pat, numbers pat, shc_grid.jdf)")
    raw = read_pat_raw(os.path.join(layout_dir, "shc_field.pat"))
    with open(os.path.join(layout_dir, "shc_field.pat")) as f:
        all_names = re.findall(r"^D (\S+?)(?:,|$)", f.read(), flags=re.M)
    text = open(os.path.join(layout_dir, "shc_grid.ctl")).read()
    draws = re.findall(r"^draw\((\S+)\)", text, flags=re.M)
    print(f"  shc_grid.ctl: {len(draws)} draws per field, pat structures not drawn "
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
    jdf = open(os.path.join(layout_dir, "shc_grid.jdf")).read()
    print(f"  shc_grid.jdf places: {re.findall(r'P\(\d\) .(\S+?).\s', jdf)}")


if __name__ == "__main__":
    layout = sys.argv[1]
    with open(os.path.join(layout, "shc_field_devices.csv")) as f:
        rows = list(csv.DictReader(f))
    check_geometry(layout, read_pat(os.path.join(layout, "shc_field.pat")), rows)
    check_files(layout)
