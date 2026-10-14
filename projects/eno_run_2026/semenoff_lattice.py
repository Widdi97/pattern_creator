"""EnO run 2026, 3-QW wafer: Semenoff (staggered honeycomb) lattices for detection-SLM
Berry-curvature tomography (FlexFund "Topo-scan"). Physics source:
tep_polariton_gpe_code/projects/full_ab_initio/EnO_run_2026/flex_fund_slm_berry_curvature/
(model_definitions.py geometry, 04_final_design.py optimum, report/).

Same workflow and field arrangement as stretched_honeycomb.py (user 2026-10-13: "analogous to
the one done already for the stretched honeycomb blueshift project"): one 500 um write field
per chip, left column 2024 overlap-series dimers (17) + 2024 50 x 50 um mesa (18) + chip x/y
numbers with the 2024 arrows (user: overlap series "2024 verbatim"); 4 x 4 lattice grid to the
right, rows = diameter staggering eta_d (top row eta = 0, plain honeycomb reference),
columns = v = a / d_mean (user: grid "eta_d x v"); one grid ctl (sem_grid.ctl) writes the
field grid with the field x/y index labels; jdf/sdf and KLayout gds as for stretched honey.

Geometry convention (model_definitions.py, geometry_research_directive.md):
nearest-neighbour A-B centre distance a = v d_mean, d_A = d_mean (1 + eta/2) (larger pillar),
d_B = d_mean (1 - eta/2); Bravais a1 = sqrt(3) a (1, 0), a2 = sqrt(3) a (1/2, sqrt(3)/2);
basis A at (0, 0), B at (0, a) -> zigzag rows along x, NN bonds at 90 and +-30 deg,
K points along k_x (orientation of all band/Berry-curvature figures of the report).
Lattices are built with generate_pattern.Lattice exactly like the 2024 KPZ lattices and
stretched_honeycomb.py (eno_tools.lattice_structures: smallest rectangular unit cell
sqrt(3) a x 3 a, D-line repetition, seam/overlap fixes). Pillars with v < 1 overlap (A-B
union raster inside each cell); v values within +-0.015 of 1 (necks/gaps of a few raster
steps) are not used.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import eno_tools as T  # noqa: E402
from generate_pattern import circle  # noqa: E402
from stretched_honeycomb import (reference_structures, shifted_numbers, place, NUMBERS_SHIFT, LEFT_X0,  # noqa: E402
                                 GRID_X0, COL_PITCH, GRID_TOP, ROW_PITCH, STREET_UM)

SYSTEM = "sem"
CHIP = "sem_field"
PIXEL = 25            # Lattice max_step_size (as stretched honey / 2024 EnO)
LATTICE_NM = 90_000   # Lattice x_size = y_size (as stretched honey: 4 x 4 in one write field)

# ---- design (filled from the GPE optimum, flex_fund_slm_berry_curvature/results/04_final_design.json)
D_MEAN = None         # nm, all lattices
DEPTH_MEV = None      # target etch depth (one per wafer), documentation only
ETA_VALUES = None     # rows, top to bottom; first = 0 (plain honeycomb)
V_VALUES = None       # columns, left to right
SOURCE_JSON = os.environ.get("SEMENOFF_DESIGN_JSON", os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "tep_polariton_gpe_code", "projects", "full_ab_initio", "EnO_run_2026",
    "flex_fund_slm_berry_curvature", "results", "04_final_design.json")))
OUT_DIR = os.environ.get("SEMENOFF_LAYOUT_OUT", os.path.join(HERE, "ecp_layout", "semenoff_slm"))

GRID_NX, GRID_NY = 3, 2   # field copies in sem_grid.ctl (user adjusts; keep small for ECP checks)


def load_design():
    import json
    global D_MEAN, DEPTH_MEV, ETA_VALUES, V_VALUES
    d = json.load(open(SOURCE_JSON))
    D_MEAN = 1000.0 * d["layout"]["d_mean_um"]
    DEPTH_MEV = d["layout"]["depth_meV"]
    ETA_VALUES = tuple(d["layout"]["eta_rows"])
    V_VALUES = tuple(d["layout"]["v_cols"])
    return d


def lattice(name, d_mean, eta, v):
    a = d_mean * v
    dA, dB = d_mean * (1 + eta / 2), d_mean * (1 - eta / 2)
    a1 = np.sqrt(3) * a * np.array([1.0, 0.0])
    a2 = np.sqrt(3) * a * np.array([0.5, np.sqrt(3) / 2])
    bs = np.array([[0.0, 0.0], [0.0, a]])
    structures, lat = T.lattice_structures(a1, a2, LATTICE_NM, LATTICE_NM, PIXEL,
                                           [[circle, 0, 0, dA / 2], [circle, 0, 0, dB / 2]], bs,
                                           fix_corner_offset=True)  # corners are non-empty here
    allr = np.concatenate([T.expand_repeat(r, rep) for _, r, rep in structures])
    mid = (allr[:, :2].min(0) + allr[:, 2:].max(0)) / 2
    ax, ay = lat.A_x[0], lat.A_y[1]
    gap = a - (dA + dB) / 2
    if gap < 0:   # overlap: neck width of the two circles at the radical axis
        RA, RB = dA / 2, dB / 2
        xr = (a * a + RA * RA - RB * RB) / (2 * a)
        neck = 2 * np.sqrt(max(RA * RA - xr * xr, 0.0))
    else:
        neck = 0.0
    return {"name": name, "structures": structures, "pixel": PIXEL, "marks": {"centre": tuple(mid)},
            "params": {"d_mean_nm": round(d_mean, 2), "eta_d": round(eta, 4), "v_a_over_dmean": round(v, 4),
                       "a_nn_nm": round(a, 2), "d_A_nm": round(dA, 2), "d_B_nm": round(dB, 2),
                       "lattice_const_nm": round(np.sqrt(3) * a, 2), "gap_AB_nm": round(gap, 1),
                       "neck_width_nm": round(neck, 1), "unit_cell_nm": f"{ax:.2f}x{ay:.2f}",
                       "period_written_nm": f"{int(ax)}x{int(ay)}",
                       "unit_cells": f"{int(lat.x_ruc_steps)}x{int(lat.y_ruc_steps)}"}}


def field_layout():
    devs, label = [], 1
    for row, eta in enumerate(ETA_VALUES):
        for col, v in enumerate(V_VALUES):
            if abs(v - 1.0) < 0.015:
                raise ValueError(f"v = {v}: A-B gap/neck of a few raster steps renders inconsistently")
            dev = lattice(f"e{eta:.3f}_v{v:.3f}".replace(".", "p"), D_MEAN, eta, v)
            dev["system"] = SYSTEM
            devs.append(place(dev, GRID_X0 + col * COL_PITCH, GRID_TOP - row * ROW_PITCH, str(label)))
            label += 1
    dimers, mesa, arrows = reference_structures()
    devs.append(place(dimers, LEFT_X0, GRID_TOP, None))  # no device numbers on references (as stretched honey)
    devs.append(place(mesa, LEFT_X0, GRID_TOP - 75_000, None))
    devs.append(arrows)
    return devs


if __name__ == "__main__":
    src = load_design()
    HEADER = [
        "Etch and overgrow 2026 (3-QW wafer), Semenoff (staggered honeycomb) lattices, detection-SLM Berry curvature",
        "generated by pattern_creator/projects/eno_run_2026/semenoff_lattice.py",
        f"target etch depth {DEPTH_MEV:g} meV; mean pillar diameter {D_MEAN:.0f} nm for all lattices",
        "4 x 4 grid: rows eta_d = (d_A - d_B)/d_mean = " + " / ".join(f"{e:.3f}" for e in ETA_VALUES)
        + " (top row = plain honeycomb), columns v = a/d_mean = " + " / ".join(f"{v:.3f}" for v in V_VALUES),
        "a = A-B centre distance; a1 = sqrt(3) a (1,0); A (0,0) diameter d_A, B (0,a) diameter d_B; K along x",
        "units nm; exposed area = pillar mesas; 25 nm raster, I 16, C 100 (as 2024 EnO lattices)",
        "lattices: generate_pattern.Lattice (bulk with D-line repetition + edge/corner structures),",
        "trimmed so that no area is exposed twice; parameters in sem_field_devices.csv",
    ]
    out = OUT_DIR
    info = T.write_chip(out, CHIP, [field_layout()], HEADER, write_ctl=False,
                        numbers_box=(NUMBERS_SHIFT[0] + 20_000, NUMBERS_SHIFT[1],
                                     NUMBERS_SHIFT[0] + 52_000, NUMBERS_SHIFT[1] + 60_000))
    shifted_numbers(os.path.join(HERE, "inputs", "numbers_xy.pat"), os.path.join(out, "numbers_sem.pat"),
                    *NUMBERS_SHIFT)
    pitch = int(T.FIELD_NM / 1000 + STREET_UM)
    T.grid_ctl(os.path.join(out, "sem_grid.ctl"), CHIP, info["structures"][0], GRID_NX, GRID_NY, pitch, pitch,
               header=HEADER, numbers_file="numbers_sem")
    dwells, incs = T.pat_dwells(os.path.join(out, f"{CHIP}.pat"), os.path.join(out, "numbers_sem.pat"))
    if len(incs) != 1:
        raise RuntimeError(f"mixed increments {incs}: RESIST/MODULAT rule needs one increment")
    T.job_jdf(os.path.join(out, "sem_grid.jdf"), "sem_grid", dwells, increment=incs.pop())
    print(f"{CHIP}: {len(info['devices'])} devices in one 500 um write field; sem_grid.ctl: "
          f"{GRID_NX} x {GRID_NY} fields at {pitch} um pitch")
    for r in info["devices"]:
        print(f"  {r['label']:>3} {r['structure']:<32} {r['width_um']:5.1f} x {r['height_um']:5.1f} um  "
              f"cells {r.get('unit_cells', ''):>6}  eta {r.get('eta_d', ''):>6} v {r.get('v_a_over_dmean', ''):>6} "
              f"gap {r.get('gap_AB_nm', ''):>7} neck {r.get('neck_width_nm', ''):>7}")
