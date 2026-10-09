"""EnO run 2026: stretched honeycomb (Kekule) lattices for pump-blueshift-induced
edge states (tep_polariton_gpe_code/.../EnO_run_2026/adiabatic_topology_blueshift).

One write field per chip, modelled on the 2024 KPZ tight-binding field
(projects/etch_and_overgrow_kpz/pattern_generation_kzp_tb): periodic lattices
written with ECP D-line repetition, all devices inside one field (one stage
operation per field), field x/y index labels from numbers_xy.pat drawn by the same
grid ctl (shc_grid.ctl: field + labels at every grid position), and
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
definition), x_size = y_size = 90 um. Touching or overlapping pillars are one
union raster inside each cell. eno_tools.lattice_structures closes the top/right
edge seams (int(A) repetition vs exact A) and trims <= 1 nm double-exposed
slivers, so no area is exposed twice. Empty edge/corner structures are not written.
"""
import os
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
LATTICE_NM = 90_000  # Lattice x_size = y_size (user: ~90 x 90 um, 4 x 4 in one write field)

D_PILLAR = 2050.0                         # nm, all lattices (user)
V_VALUES = np.linspace(1.1, 1.2, 4)       # x direction of the grid
S_VALUES = (0.0, 80.0, 110.0, 140.0)      # nm, y direction of the grid

GRID_NX, GRID_NY = 3, 2  # field copies in shc_grid.ctl (user adjusts; keep small for ECP checks)
STREET_UM = 50           # free space between neighbouring fields (pitch = 500 + 50 um)


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


# Explicit field arrangement (nm), like the fixed lattice grid of the 2024 KPZ field
# (user sketch 2026-10-09): left column from the top: 2024 overlap dimers, 2024
# 50 um mesa, chip x/y numbers + arrows; 4 x 4 lattice grid right of it
# (columns = v, rows = s, top row s = 0).
LEFT_X0 = 10_000
GRID_X0, COL_PITCH = 75_000, 103_000
GRID_TOP, ROW_PITCH = 490_000, 118_000
NUMBERS_SHIFT = (-10_000, 230_000)  # numbers_xy.pat glyphs (x 20-52, y 0-60 um) -> x 10-42, y 230-290 um


def place(dev, x_left, y_top, label):
    """Put the device bbox top-left at (x_left, y_top); its number label below it."""
    bx1, by1, bx2, by2 = T.dev_bbox(dev)
    dev = dict(dev, system=dev.get("system", SYSTEM), label=label,
               pos=(int(round(x_left - bx1)), int(round(y_top - by2))),
               label_pos=(x_left, y_top - (by2 - by1) - T.LABEL_GAP_NM - T.LABEL_NM))
    return dev


def reference_structures():
    """2024 KPZ overlap series split into its dimer block and its 50 x 50 um mesa
    (verbatim rects, translated only), plus arrow_right / arrow_up placed right of
    the shifted field x / y index labels."""
    pat = read_pat(os.path.join(HERE, "inputs", "other_patterns_kpz_tb_2024.pat"), expand=False)
    ov = pat["overlap_series"]
    dimers = ov[ov[:, 2] <= 130_000]
    mesa = ov[ov[:, 0] >= 140_000]
    if len(dimers) + len(mesa) != len(ov):
        raise RuntimeError("overlap_series split lost rectangles")
    dimer_dev = {"name": "overlap_dimers_2024", "system": "ref", "structures": [("", dimers, None)],
                 "params": {"note": "2024 KPZ overlap_series dimers: d 1.8 / 2.1 um, v 0.4-1.3"}}
    mesa_dev = {"name": "mesa_50um_2024", "system": "ref", "structures": [("", mesa, None)],
                "params": {"note": "2024 KPZ overlap_series 50 x 50 um planar mesa"}}
    # nbr_x_: y 35-60 um, nbr_y_: y 0-25 um, both right-aligned at x 52 um (+ NUMBERS_SHIFT);
    # arrows start 4 / 6 um right of the digits and are centred on them
    nx_, ny_ = NUMBERS_SHIFT
    right = pat["arrow_right"] + np.array([nx_ + 19_875, ny_ + 2_375] * 2)  # x 46.0-61.75 um
    up = pat["arrow_up"] + np.array([nx_ + 16_875, ny_ + 2_500] * 2)        # x 48.0-54.0 um
    arrows = {"name": "arrows", "system": "ref", "pos": (0, 0),
              "structures": [("right", right, None), ("up", up, None)],
              "params": {"note": "2024 arrow_right (next to field x index) and arrow_up (next to field y index)"}}
    return dimer_dev, mesa_dev, arrows


def shifted_numbers(src, dst, dx, dy):
    """numbers_xy.pat (2024 chip x/y labels, 'P 0, x1, y1, x2, y2') shifted by (dx, dy) nm."""
    out = []
    for line in open(src):
        if line.startswith("P 0,"):
            c = [int(v) for v in line[2:].split(",")]
            line = f"P 0, {c[1] + dx}, {c[2] + dy}, {c[3] + dx}, {c[4] + dy}\n"
        out.append(line)
    with open(dst, "w") as f:
        f.write(f"; numbers_xy.pat of the 2024 EnO layout, shifted by ({dx}, {dy}) nm (stretched_honeycomb.py)\n")
        f.write("".join(out))


def field_layout():
    devs, label = [], 1
    for row, s in enumerate(S_VALUES):
        for col, v in enumerate(V_VALUES):
            dev = lattice(f"v{v:.3f}_s{int(s):03d}".replace(".", "p"), D_PILLAR, v, s)
            devs.append(place(dev, GRID_X0 + col * COL_PITCH, GRID_TOP - row * ROW_PITCH, str(label)))
            label += 1
    dimers, mesa, arrows = reference_structures()
    devs.append(place(dimers, LEFT_X0, GRID_TOP, None))  # no device numbers on references (user)
    devs.append(place(mesa, LEFT_X0, GRID_TOP - 75_000, None))
    devs.append(arrows)
    return devs


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
    info = T.write_chip(out, CHIP, [field_layout()], HEADER, write_ctl=False,
                         numbers_box=(NUMBERS_SHIFT[0] + 20_000, NUMBERS_SHIFT[1],
                                      NUMBERS_SHIFT[0] + 52_000, NUMBERS_SHIFT[1] + 60_000))
    shifted_numbers(os.path.join(HERE, "inputs", "numbers_xy.pat"), os.path.join(out, "numbers_shc.pat"),
                    *NUMBERS_SHIFT)
    pitch = int(T.FIELD_NM / 1000 + STREET_UM)
    T.grid_ctl(os.path.join(out, "shc_grid.ctl"), CHIP, info["structures"][0], GRID_NX, GRID_NY, pitch, pitch,
               header=HEADER, numbers_file="numbers_shc")
    dwells, incs = T.pat_dwells(os.path.join(out, f"{CHIP}.pat"), os.path.join(out, "numbers_shc.pat"))
    if len(incs) != 1:
        raise RuntimeError(f"mixed increments {incs}: RESIST/MODULAT rule needs one increment")
    T.job_jdf(os.path.join(out, "shc_grid.jdf"), "shc_grid", dwells, increment=incs.pop())
    print(f"{CHIP}: {len(info['devices'])} devices in one 500 um write field; shc_grid.ctl: "
          f"{GRID_NX} x {GRID_NY} fields at {pitch} um pitch")
    for r in info["devices"]:
        print(f"  {r['label']:>3} {r['structure']:<32} {r['width_um']:5.1f} x {r['height_um']:5.1f} um  "
              f"cells {r.get('unit_cells', ''):>5}  v {r.get('v_a_over_d', ''):>6} s {r.get('s_nm', ''):>6} "
              f"gap {r.get('inter_gap_nm', ''):>6}")



