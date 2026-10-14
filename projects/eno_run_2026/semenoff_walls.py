"""EnO run 2026, 3-QW wafer: Semenoff mass domain walls for valley-Hall transport (second write field).

Physics source: tep_polariton_gpe_code/projects/full_ab_initio/EnO_run_2026/flex_fund_slm_berry_curvature/
07_domain_wall_ribbons.py (ribbon Bloch bands) and the report section "Mass domain walls". User 2026-10-14: "we also
want to investigate semenoff transport interfaces where the mass changes sign. do we need a small atom or large atom
interface? Design both".

Geometry (model_definitions.py of the GPE project): honeycomb with A-B distance a = v d_mean, a1 = sqrt(3) a (1, 0),
row j: A_j at (j sqrt(3) a/2 mod sqrt(3) a, 1.5 a j), B_j = A_j + (0, a); zigzag rows along x. Below the wall
(domain I) A is the large pillar (d_A = d_mean (1 + eta/2)), above it (domain II) the diameters are swapped, so the
Semenoff mass changes sign at the wall. Wall families as in the ribbon calculation:
  chain : the wall cuts the two 30 deg bonds between B_j and A_{j+1}: the pillars along the wall form a zigzag chain
          of equal size -> large-atom (LL) or small-atom (SS) chain wall
  dimer : the wall cuts the vertical bond A_j - B_j: equal-size dimers across the wall
Wall type: which domain lies below decides LL vs SS (chain: domain II below -> LL; dimer: domain I below -> LL).
Each lattice is a rectangle ~ LATTICE_NM x LATTICE_NM with the wall along x through its middle; only whole pillars
(centre inside the rectangle). Pillars are rasterised from the explicit disk list (eno_tools.shapes_to_rects, 25 nm,
union of overlapping disks, exact non-overlapping column rects) - same site construction as the GPE ribbon; no D-line
repetition, so no seams. One 500 um write field; grid ctl with the field index labels as for the bulk field.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import eno_tools as T  # noqa: E402
from stretched_honeycomb import shifted_numbers, place, NUMBERS_SHIFT, GRID_X0, COL_PITCH, GRID_TOP, ROW_PITCH, \
    STREET_UM, reference_structures  # noqa: E402

SYSTEM = "dw"
CHIP = "semw_field"
PIXEL = 25
LATTICE_NM = 90_000
SOURCE_JSON = os.environ.get("SEMENOFF_DESIGN_JSON", os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "tep_polariton_gpe_code", "projects", "full_ab_initio", "EnO_run_2026",
    "flex_fund_slm_berry_curvature", "results", "04_final_design.json")))
OUT_DIR = os.environ.get("SEMENOFF_WALLS_OUT", os.path.join(HERE, "ecp_layout", "semenoff_walls"))
ETA_ROWS = (0.29, 0.22)                                    # rows (top to bottom); 0.29 = recommended bulk design
WALLS = (("chain", "LL"), ("chain", "SS"), ("dimer", "LL"), ("dimer", "SS"))   # columns
GRID_NX, GRID_NY = 3, 2


def wall_lattice(name, d_mean, eta, v, family, kind, size=LATTICE_NM):
    a = d_mean * v
    Lx = np.sqrt(3) * a
    dA, dB = d_mean * (1 + eta / 2), d_mean * (1 - eta / 2)
    n_rows = int(size // (1.5 * a))
    jw = n_rows // 2 - 1                                    # wall right after row jw
    yw = 1.5 * a * jw + (0.5 * a if family == "dimer" else 1.25 * a)
    below_is_I = (family == "dimer") == (kind == "LL")    # chain LL / dimer SS: domain II below the wall
    shapes, sites = [], []
    n_cols = int(size // Lx) + 1
    for j in range(n_rows):
        for lab, yy in ((0, 1.5 * a * j), (1, 1.5 * a * j + a)):
            in_I = (yy < yw) == below_is_I
            big = (lab == 0) == in_I                        # domain I: A large; domain II: B large
            d = dA if big else dB
            for i in range(-1, n_cols + 1):
                xx = (j % 2) * Lx / 2 + i * Lx
                if 0 <= xx <= size and yy <= 1.5 * a * (n_rows - 1) + a:
                    shapes.append(("circle", xx, yy, d))
                    sites.append((xx, yy, d, int(big), int(lab), int(yy > yw)))
    sites = np.array(sites)
    # pillars on the bonds crossing the wall: size check of the wall type
    near = np.abs(sites[:, 1] - yw) < 0.6 * a
    big_w = sites[near, 3]
    if not ((kind == "LL" and big_w.all()) or (kind == "SS" and (big_w == 0).all())):
        raise RuntimeError(f"{name}: wall pillars are not all {kind}")
    gap = a - d_mean
    return {"name": name, "shapes": shapes, "pixel": PIXEL, "sites": sites,
            "marks": {"wall_left": (0.0, yw), "wall_right": (float(size), yw)},
            "params": {"family": family, "wall": kind, "d_mean_nm": round(d_mean, 2), "eta_d": round(eta, 4),
                       "v_a_over_dmean": round(v, 4), "a_nn_nm": round(a, 2), "d_A_nm": round(dA, 2),
                       "d_B_nm": round(dB, 2), "lattice_const_nm": round(Lx, 2), "gap_AB_nm": round(gap, 1),
                       "rows": n_rows, "pillars": len(sites), "wall_y_local_nm": round(yw, 1)}}


def field_layout(d_mean, v):
    devs, label, all_sites = [], 1, {}
    for row, eta in enumerate(ETA_ROWS):
        for col, (fam, kind) in enumerate(WALLS):
            name = f"{fam}{kind}_e{eta:.3f}".replace(".", "p")
            dev = wall_lattice(name, d_mean, eta, v, fam, kind)
            dev["system"] = SYSTEM
            placed = place(dev, GRID_X0 + col * COL_PITCH, GRID_TOP - row * ROW_PITCH, str(label))
            bx1, by1, _, _ = T.dev_bbox(dev)
            all_sites[name] = dev["sites"] + np.array([placed["pos"][0], placed["pos"][1], 0, 0, 0, 0])
            devs.append(placed)
            label += 1
    _, _, arrows = reference_structures()                  # 2024 arrows next to the field index labels
    devs.append(arrows)
    return devs, all_sites


if __name__ == "__main__":
    fd = json.load(open(SOURCE_JSON))
    d_mean = 1000.0 * fd["layout"]["d_mean_um"]
    v = float(fd["design"]["v"])
    depth = fd["layout"]["depth_meV"]
    HEADER = [
        "Etch and overgrow 2026 (3-QW wafer), Semenoff mass domain walls (valley-Hall transport), second field",
        "generated by pattern_creator/projects/eno_run_2026/semenoff_walls.py",
        f"target etch depth {depth:g} meV; d_mean {d_mean:.0f} nm, v = a/d_mean = {v:.3f} (bulk design), eta rows "
        + " / ".join(f"{e:.2f}" for e in ETA_ROWS),
        "columns: chain LL, chain SS, dimer LL, dimer SS walls (along x, through the middle of each lattice)",
        "below the wall A large, above swapped (or vice versa, see devices csv); whole pillars only",
        "units nm; exposed area = pillar mesas; 25 nm raster, I 16, C 100 (as 2024 EnO lattices); explicit disks",
    ]
    devs, all_sites = field_layout(d_mean, v)
    info = T.write_chip(OUT_DIR, CHIP, [devs], HEADER, write_ctl=False,
                        numbers_box=(NUMBERS_SHIFT[0] + 20_000, NUMBERS_SHIFT[1],
                                     NUMBERS_SHIFT[0] + 52_000, NUMBERS_SHIFT[1] + 60_000))
    shifted_numbers(os.path.join(HERE, "inputs", "numbers_xy.pat"), os.path.join(OUT_DIR, "numbers_semw.pat"),
                    *NUMBERS_SHIFT)
    pitch = int(T.FIELD_NM / 1000 + STREET_UM)
    T.grid_ctl(os.path.join(OUT_DIR, "semw_grid.ctl"), CHIP, info["structures"][0], GRID_NX, GRID_NY, pitch, pitch,
               header=HEADER, numbers_file="numbers_semw")
    dwells, incs = T.pat_dwells(os.path.join(OUT_DIR, f"{CHIP}.pat"), os.path.join(OUT_DIR, "numbers_semw.pat"))
    T.job_jdf(os.path.join(OUT_DIR, "semw_grid.jdf"), "semw_grid", dwells, increment=incs.pop())
    np.savez(os.path.join(OUT_DIR, "semw_sites.npz"), **{k: v_ for k, v_ in all_sites.items()})
    print(f"{CHIP}: {len(info['devices'])} devices; semw_grid.ctl {GRID_NX} x {GRID_NY} at {pitch} um")
    for r in info["devices"]:
        print(f"  {r['label']:>3} {r['structure']:<34} {r['width_um']:5.1f} x {r['height_um']:5.1f} um  "
              f"{r.get('family', ''):>5} {r.get('wall', ''):>2} eta {r.get('eta_d', ''):>5} pillars {r.get('pillars', ''):>5} "
              f"rects {r['n_rects_written']}")
