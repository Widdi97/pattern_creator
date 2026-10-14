"""Verify the Semenoff ECP files against the GPE geometry and against each other.

1. Geometry, per lattice of sem_field_devices.csv (works for separate and for overlapping,
   merged pillars): the written pattern (D-line repetition expanded) is painted on a 5 nm
   grid in a window of WIN_CELLS x WIN_CELLS rectangular cells around the lattice centre and
   compared with the analytic union of disks of the GPE construction
   (flex_fund_slm_berry_curvature/model_definitions.py: a = v d_mean, d_A/B = d_mean (1 +- eta/2),
   a1 = sqrt(3) a (1, 0), a2 = sqrt(3) a (1/2, sqrt(3)/2), A at 0, B at (0, a)).
   The lattice offset is found by FFT cross-correlation (no assumption on the Lattice origin).
   Reported: area mismatch |pattern XOR GPE| / GPE area, and per sublattice the exposed area
   inside its power-diagram cell vs the analytic disk-in-cell area, expressed as an
   equivalent-diameter error, plus the centroid offset of each sublattice.
2. Files: sem_grid.ctl draws every structure of the pat once per field, number structures
   exist, ends with END, jdf places sem_grid.v30 (verify_layout.check_files logic).

usage: python verify_semenoff.py <layout_dir>
"""
import csv
import os
import re
import sys

import numpy as np

from check_pat import read_pat, read_pat_raw

PIX = 5           # nm
WIN_CELLS = 3     # analysis window in rectangular cells (sqrt(3) a x 3 a)


def paint(rects, x0, y0, nx, ny):
    m = np.zeros((ny, nx), dtype=bool)
    sel = (rects[:, 2] > x0) & (rects[:, 0] < x0 + nx * PIX) & (rects[:, 3] > y0) & (rects[:, 1] < y0 + ny * PIX)
    for a, b, c, d in rects[sel]:
        i1, i2 = max((a - x0) // PIX, 0), min((c - x0) // PIX, nx)
        j1, j2 = max((b - y0) // PIX, 0), min((d - y0) // PIX, ny)
        m[j1:j2, i1:i2] = True
    return m


def analytic(nx, ny, Lx, Ly, a, RA, RB):
    """Union-of-disks mask and A power-cell region on a periodic window of nx x ny pixels
    (window = integer number of cells). Each site only touches the pixels within 1.6 R."""
    xs, ys = (np.arange(nx) + 0.5) * PIX, (np.arange(ny) + 0.5) * PIX
    sites = [(Lx / 4, a / 2, RA, 0), (Lx / 4, 1.5 * a, RB, 1), (0.75 * Lx, 2 * a, RA, 0), (0.75 * Lx, 0.0, RB, 1)]
    Wx, Wy = nx * PIX, ny * PIX
    inside = np.zeros((ny, nx), bool)
    powr = [np.full((ny, nx), np.inf), np.full((ny, nx), np.inf)]
    reach = 1.6 * max(RA, RB) + a   # power-cell boundaries lie within this distance of a site
    for i in range(-1, int(round(Wx / Lx)) + 1):
        for j in range(-1, int(round(Wy / Ly)) + 1):
            for cx, cy, R, lab in sites:
                px, py = cx + i * Lx, cy + j * Ly
                i1, i2 = np.searchsorted(xs, [px - reach, px + reach])
                j1, j2 = np.searchsorted(ys, [py - reach, py + reach])
                if i2 <= i1 or j2 <= j1:
                    continue
                X, Y = np.meshgrid(xs[i1:i2], ys[j1:j2])
                d2 = (X - px) ** 2 + (Y - py) ** 2
                inside[j1:j2, i1:i2] |= d2 < R * R
                np.minimum(powr[lab][j1:j2, i1:i2], d2 - R * R, out=powr[lab][j1:j2, i1:i2])
    return inside, powr[0] < powr[1]


def check_geometry(pat, rows):
    print("== geometry vs GPE construction (model_definitions.py)")
    worst = 0.0
    for row in rows:
        if "_sem_" not in row["structure"]:
            continue
        d, eta, v = float(row["d_mean_nm"]), float(row["eta_d"]), float(row["v_a_over_dmean"])
        a = d * v
        RA, RB = d * (1 + eta / 2) / 2, d * (1 - eta / 2) / 2
        Lx, Ly = np.sqrt(3) * a, 3 * a
        rects = np.concatenate([rr for name, rr in pat.items() if name.startswith(row["structure"] + "_x_")])
        # window: WIN_CELLS cells, pixel counts chosen so that the window is (very nearly) periodic
        nx = int(round(WIN_CELLS * Lx / PIX))
        ny = int(round(WIN_CELLS * Ly / PIX))
        cx, cy = float(row["x_centre_um"]) * 1000, float(row["y_centre_um"]) * 1000
        x0, y0 = int(cx - nx * PIX / 2), int(cy - ny * PIX / 2)
        m = paint(rects, x0, y0, nx, ny)
        ref, regA = analytic(nx, ny, nx * PIX / WIN_CELLS, ny * PIX / WIN_CELLS, a * (nx * PIX / WIN_CELLS) / Lx,
                             RA, RB)
        # best periodic shift of the analytic mask onto the pattern
        F = np.fft.ifft2(np.fft.fft2(m.astype(float)) * np.conj(np.fft.fft2(ref.astype(float)))).real
        sy, sx = np.unravel_index(np.argmax(F), F.shape)
        ref_s, regA_s = np.roll(ref, (sy, sx), axis=(0, 1)), np.roll(regA, (sy, sx), axis=(0, 1))
        mism = np.sum(m ^ ref_s) / np.sum(ref_s)
        out = []
        for lab, reg in (("A", regA_s), ("B", ~regA_s)):
            got, want = np.sum(m & reg), np.sum(ref_s & reg)
            r_exp = RA if lab == "A" else RB
            # d(area)/dR ~ 2 pi R per pillar -> equivalent diameter error
            n_p = 2 * WIN_CELLS * WIN_CELLS
            dD = 2 * (got - want) * PIX * PIX / n_p / (2 * np.pi * r_exp)
            Yg, Xg = np.nonzero(m & reg)
            Yw, Xw = np.nonzero(ref_s & reg)
            dc = np.hypot(Xg.mean() - Xw.mean(), Yg.mean() - Yw.mean()) * PIX
            out.append(f"{lab}: d_eq err {dD:+6.1f} nm, centroid {dc:5.1f} nm")
            worst = max(worst, abs(dD))
        print(f"  {row['label']:>2} {row['structure'][len('sem_field_f0_sem_'):]:<16} eta {eta:.3f} v {v:.3f}: "
              f"XOR mismatch {100 * mism:5.2f} % of GPE area | " + " | ".join(out))
    print(f"  worst equivalent-diameter error: {worst:.1f} nm")


def check_files(layout_dir):
    print("== file consistency (sem_grid.ctl, sem_field.pat, numbers_sem.pat, sem_grid.jdf)")
    raw = read_pat_raw(os.path.join(layout_dir, "sem_field.pat"))
    with open(os.path.join(layout_dir, "sem_field.pat")) as f:
        all_names = re.findall(r"^D (\S+?)(?:,|$)", f.read(), flags=re.M)
    text = open(os.path.join(layout_dir, "sem_grid.ctl")).read()
    draws = re.findall(r"^draw\((\S+)\)", text, flags=re.M)
    print(f"  sem_grid.ctl: {len(draws)} draws per field, pat structures not drawn "
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
    jdf = open(os.path.join(layout_dir, "sem_grid.jdf")).read()
    print(f"  sem_grid.jdf places: {re.findall(r'P\(\d\) .(\S+?).\s', jdf)}")


if __name__ == "__main__":
    layout = sys.argv[1]
    with open(os.path.join(layout, "sem_field_devices.csv")) as f:
        rows = list(csv.DictReader(f))
    check_geometry(read_pat(os.path.join(layout, "sem_field.pat")), rows)
    check_files(layout)
