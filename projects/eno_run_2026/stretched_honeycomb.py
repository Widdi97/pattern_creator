"""EnO run 2026: stretched honeycomb (Kekule) lattices for pump-blueshift-induced
edge states (tep_polariton_gpe_code/.../EnO_run_2026/adiabatic_topology_blueshift).

One write field per chip, modelled on the 2024 KPZ tight-binding field
(projects/etch_and_overgrow_kpz/pattern_generation_kzp_tb): periodic lattices
written with ECP D-line repetition, all devices inside one field (one stage
operation per chip), chip x/y numbers from numbers_xy.pat (separate ctl), and
the 2024 molecule overlap series including its 50 x 50 um planar mesa.

Geometry convention (gpe_v3.py:80-90): a = d*v, a_latt = 3a; six pillars per
hexamer at radius a + s, angles 0, 60, ..., 300 deg; hexamer centres on the
triangular lattice a_latt (1, 0), a_latt (1/2, sqrt(3)/2). Intra-hexamer centre
distance a + s, inter-hexamer (short, pump-cut) distance a - 2s.

Parameter grid (user 2026-10-09, one etch depth, target 18 meV): pillar
diameter fixed at 2050 nm for all lattices; 4 x 4 grid, columns = overlap
v = 1.1 ... 1.2 (4 equal steps), rows = stretch s = 0, 80, 110, 140 nm. It
brackets the GPE optima of gpe_v3.py: set #1 (17.50 meV: d 2019 nm, v 1.118,
s 103 nm) and set #3 (18.80 meV: d 2071 nm, v 1.181, s 141 nm).

Lattices are built exactly like the 2024 KPZ tight-binding lattices
(pattern_generation_kzp_tb/patterns_lattices.py): generate_pattern.Lattice with
the GPE basis [[circle, 0, 0, r]] x 6 at b_k = (a + s)(cos 60k, sin 60k), which
finds the smallest rectangular unit cell (a_latt x sqrt(3) a_latt) and writes the
bulk with D-line repetition plus edge and corner structures (its boundary
definition), x_size = y_size = 80 um. Touching or overlapping pillars are one
union raster inside each cell. eno_tools.lattice_structures closes the top/right
edge seams (int(A) repetition vs exact A) and trims <= 1 nm double-exposed
slivers, so no area is exposed twice. Empty edge/corner structures are not written.
"""
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import eno_tools as T  # noqa: E402
from check_pat import read_pat  # noqa: E402
from generate_pattern import circle  # noqa: E402

SYSTEM = "kek"
CHIP = "shc_field"
PIXEL = 25           # Lattice max_step_size (user: 25 nm is sufficient)
LATTICE_NM = 80_000  # Lattice x_size = y_size (user: 80 x 80 um)

D_PILLAR = 2050.0                         # nm, all lattices (user)
V_VALUES = np.linspace(1.1, 1.2, 4)       # x direction of the grid
S_VALUES = (0.0, 80.0, 110.0, 140.0)      # nm, y direction of the grid

REGION_UM = 27_000  # placeholder array for the jdf; copies are set manually at the tool
STREET_UM = 50


def exposed(points, rects):
    """True for points lying inside any rect."""
    p = np.asarray(points, dtype=float)
    out = np.zeros(len(p), dtype=bool)
    for chunk in range(0, len(rects), 20_000):
        r = rects[chunk:chunk + 20_000]
        out |= ((p[:, None, 0] >= r[None, :, 0]) & (p[:, None, 0] < r[None, :, 2])
                & (p[:, None, 1] >= r[None, :, 1]) & (p[:, None, 1] < r[None, :, 3])).any(1)
    return out


def lattice(name, d, v, s):
    a = d * v
    a_latt = 3 * a
    a1 = a_latt * np.array([1.0, 0.0])
    a2 = a_latt * np.array([0.5, np.sqrt(3) / 2])
    R = a + s
    ang = np.deg2rad(60 * np.arange(6))
    bs = R * np.column_stack([np.cos(ang), np.sin(ang)])
    structures, lat = T.lattice_structures(a1, a2, LATTICE_NM, LATTICE_NM, PIXEL,
                                           [[circle, 0, 0, d / 2] for _ in bs], bs)
    allr = np.concatenate([T.expand_repeat(r, rep) for _, r, rep in structures])
    # lattice point (0, 0) of the first bulk cell in pattern coordinates: generate_pattern
    # draws shapes at centre - step/2 and offsets the bulk cell by round(2 A) (+ global offset 0)
    ax, ay = lat.A_x[0], lat.A_y[1]
    nx, ny = int(lat.x_ruc_steps), int(lat.y_ruc_steps)
    origin = np.array([round(2 * ax), round(2 * ay)]) - lat.step_size / 2
    hexc = np.array([origin + [i * int(ax), j * int(ay)] + h for i in range(nx) for j in range(ny)
                     for h in ([0.0, 0.0], [ax / 2, ay / 2])])
    full = np.array([exposed(c + bs, allr).all() and not exposed([c], allr)[0] for c in hexc])
    if full.sum() < 0.5 * len(hexc):
        raise RuntimeError(f"{name}: hexamer positions do not match the written pattern")
    mid = (allr[:, :2].min(0) + allr[:, 2:].max(0)) / 2
    cand = hexc[full]
    pump = cand[np.argmin(np.linalg.norm(cand - mid, axis=1))]
    inter, intra = a - 2 * s, a + s
    return {"name": name, "structures": structures, "pixel": PIXEL, "marks": {"pump_centre": tuple(pump)},
            "params": {"d_nm": round(d, 2), "v_a_over_d": round(v, 4), "a_nm": round(a, 2), "s_nm": round(s, 2),
                       "s_over_a": round(s / a, 4), "a_latt_nm": round(a_latt, 2),
                       "unit_cell_nm": f"{ax:.2f}x{ay:.2f}", "period_written_nm": f"{int(ax)}x{int(ay)}",
                       "unit_cells": f"{nx}x{ny}",
                       "intra_cc_nm": round(intra, 2), "intra_gap_nm": round(intra - d, 1),
                       "inter_cc_nm": round(inter, 2), "inter_gap_nm": round(inter - d, 1),
                       "pump_apothem_sim_um": round(0.97 * 2.7 / 2 * a_latt / 1e3, 3)}}


def grid_rows():
    """One group per stretch row (each group starts a new row): x = v, y = s."""
    rows = []
    for s in S_VALUES:
        rows.append((SYSTEM, [lattice(f"v{v:.3f}_s{int(s):03d}".replace(".", "p"), D_PILLAR, v, s)
                              for v in V_VALUES]))
    return rows


def overlap_series():
    """2024 molecule overlap series + 50 x 50 um mesa, copied verbatim (translated only)."""
    rects = read_pat(os.path.join(HERE, "inputs", "other_patterns_kpz_tb_2024.pat"), expand=False)["overlap_series"]
    rects = rects - np.array([rects[:, 0].min(), rects[:, 1].min()] * 2)
    return {"name": "overlap_series_2024", "structures": [("", rects, None)],
            "params": {"note": "2024 KPZ field overlap_series: dimers d 1.8 / 2.1 um, v 0.4-1.3, "
                               "plus 50 x 50 um planar mesa"}}


def direction_arrows():
    """2024 KPZ arrow_right / arrow_up (verbatim rects), placed right of the chip
    x/y index labels of numbers_xy.pat (nbr_x_: x 20-52 um, y 35-60 um; nbr_y_: y 0-25 um).
    Fixed position in the reserved corner, no device number."""
    pat = read_pat(os.path.join(HERE, "inputs", "other_patterns_kpz_tb_2024.pat"), expand=False)
    right = pat["arrow_right"] + np.array([19_875, 2_375] * 2)  # -> x 56.0-71.75 um, centred on nbr_x_
    up = pat["arrow_up"] + np.array([16_875, 2_500] * 2)        # -> x 58.0-64.0 um, centred on nbr_y_
    return {"name": "arrows", "system": "ref", "pos": (0, 0),
            "structures": [("right", right, None), ("up", up, None)],
            "params": {"note": "2024 arrow_right (next to field x index) and arrow_up (next to field y index)"}}


HEADER = [
    "Etch and overgrow 2026, stretched honeycomb (Kekule) lattices, pump-blueshift edge states",
    "generated by pattern_creator/projects/eno_run_2026/stretched_honeycomb.py",
    "target etch depth 18 meV; pillar diameter 2050 nm for all lattices",
    "4 x 4 grid: columns v = 1.100 / 1.133 / 1.167 / 1.200, rows stretch s = 0 / 80 / 110 / 140 nm",
    "units nm; exposed area = pillar mesas; 25 nm raster, I 16, C 100 (as 2024 EnO lattices)",
    "lattices: generate_pattern.Lattice (bulk _x_0_y_0 with D-line repetition + edge/corner structures),",
    "trimmed so that no area is exposed twice; parameters in shc_field_devices.csv",
]


if __name__ == "__main__":
    out = os.path.join(HERE, "ecp_layout", "stretched_honeycomb")
    fields, height_nm = T.pack_compact(grid_rows() + [("ref", [overlap_series()])])
    if len(fields) != 1:
        raise RuntimeError("layout must fit into one write field (one stage operation per chip)")
    arrows = direction_arrows()
    r = np.concatenate([s[1] for s in arrows["structures"]])
    if r[:, 2].max() > T.RESERVED_NM[2] or r[:, 3].max() > T.RESERVED_NM[3]:
        raise RuntimeError("arrows leave the reserved number corner")
    fields[0].append(arrows)
    info = T.write_chip(out, CHIP, fields, HEADER)
    shutil.copy(os.path.join(HERE, "inputs", "numbers_xy.pat"), os.path.join(out, "numbers_xy.pat"))
    pitch_x = int(np.ceil((info["width_um"] + STREET_UM) / 10) * 10)
    pitch_y = int(np.ceil((height_nm / 1000 + STREET_UM) / 10) * 10)
    nx, ny = min(REGION_UM // pitch_x, 98), min(REGION_UM // pitch_y, 98)
    T.numbers_ctl(os.path.join(out, "shc_numbers.ctl"), "stretched honeycomb region", nx, ny, pitch_x, pitch_y)
    T.region_jdf(os.path.join(out, "shc_region.jdf"), CHIP, "shc_numbers", nx, ny, pitch_x, pitch_y)
    names = [ln[5:-2] for ln in open(os.path.join(out, f"{CHIP}.ctl")) if ln.startswith("draw(")]
    T.grid_ctl(os.path.join(out, "shc_grid_test.ctl"), CHIP, names, 3, 2, pitch_x, pitch_y)
    print(f"{CHIP}: {len(info['devices'])} devices in one write field, chip {info['width_um']:.0f} x "
          f"{height_nm / 1000:.0f} um, placeholder array {nx} x {ny} at {pitch_x} x {pitch_y} um")
    for r in info["devices"]:
        print(f"  {r['label']:>3} {r['structure']:<32} {r['width_um']:5.1f} x {r['height_um']:5.1f} um  "
              f"cells {r.get('unit_cells', ''):>5}  v {r.get('v_a_over_d', ''):>6} s {r.get('s_nm', ''):>6} "
              f"gap {r.get('inter_gap_nm', ''):>6}")
