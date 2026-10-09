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

Target etch depth (user 2026-10-09): 18 meV, one value for the whole layout.
The two GPE sets closest to it are used with their exact gpe_v3.py values:
set #1 (E_confine 17.50 meV) and set #3 (18.80 meV, best score). Set #2
(14.59 meV) is not used. For each set: honeycomb stretch series s = f * s_opt,
f = 0, 0.5, 0.8, 1.0, 1.2 (s_opt = the set's optimised stretch), plus diameter
offsets (litho/etch bias, centres fixed) and overlap v = a/d +- 0.03 at s_opt.

Lattices are built exactly like the 2024 KPZ tight-binding lattices
(pattern_generation_kzp_tb/patterns_lattices.py): generate_pattern.Lattice with
the GPE basis [[circle, 0, 0, r]] x 6 at b_k = (a + s)(cos 60k, sin 60k), which
finds the smallest rectangular unit cell (a_latt x sqrt(3) a_latt) and writes the
bulk with D-line repetition plus edge and corner structures (its boundary
definition), x_size = y_size = 80 um. Touching or overlapping pillars (set #1 at
f = 1.2, +40 nm, v - 0.03) are one union raster inside each cell.
generate_pattern.Lattice repeats cells with int(A) while each cell's raster spans
the exact A, which can leave <= 1 nm double-exposed slivers at cell boundaries;
eno_tools.make_exposure_unique trims these (identically in every copy) so no
area is exposed twice. Empty edge/corner structures are not written.
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
PIXEL = 10           # Lattice max_step_size (resolves the 32 nm set #1 gaps; KPZ 2024 used 25)
LATTICE_NM = 80_000  # Lattice x_size = y_size (user: 80 x 80 um)

# exact gpe_v3.py parameter sets (lines 23-31 and 47-57)
SETS = {
    "set1": dict(E_confine_meV=17.50080532953143, r=1009.6936398323935, v=1.1181064672185277,
                 s=103.0599851384759, B_meV=2.9565372318029404),
    "set3": dict(E_confine_meV=18.802209774730727, r=1035.3922179910422, v=1.1808894979214528,
                 s=140.7230754001066, B_meV=2.429483210667968),
}
STRETCH_FRACTIONS = (0.0, 0.5, 0.8, 1.0, 1.2)
DIAMETER_OFFSETS = (-80, -40, 40)
DV = 0.03

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


def lattice(name, d, a, s, note, set_name, extra):
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
    n_ex = exposed((hexc[:, None, :] + bs[None]).reshape(-1, 2), allr).sum()
    inter, intra = a - 2 * s, a + s
    p = SETS[set_name]
    return {"name": name, "structures": structures, "pixel": PIXEL, "marks": {"pump_centre": tuple(pump)},
            "params": {"set": set_name, "variation": note, **extra,
                       "d_nm": round(d, 2), "a_nm": round(a, 2), "v_a_over_d": round(a / d, 5),
                       "s_nm": round(s, 2), "a_latt_nm": round(a_latt, 2),
                       "unit_cell_nm": f"{ax:.2f}x{ay:.2f}", "period_written_nm": f"{int(ax)}x{int(ay)}",
                       "supercells": f"{nx}x{ny}", "bulk_pillar_centres_exposed": int(n_ex),
                       "intra_cc_nm": round(intra, 2), "intra_gap_nm": round(intra - d, 1),
                       "inter_cc_nm": round(inter, 2), "inter_gap_nm": round(inter - d, 1),
                       "set_E_confine_meV": round(p["E_confine_meV"], 3), "set_B_meV": round(p["B_meV"], 3),
                       "pump_apothem_sim_um": round(0.97 * 2.7 / 2 * a_latt / 1e3, 3)}}


def set_devices(set_name):
    p = SETS[set_name]
    d0, v0, s0 = 2 * p["r"], p["v"], p["s"]
    a0 = d0 * v0
    devs = []
    for f in STRETCH_FRACTIONS:
        devs.append(lattice(f"{set_name}_s{int(round(100 * f)):03d}", d0, a0, f * s0,
                            f"stretch {100 * f:.0f} % of s_opt" + (" (GPE set)" if f == 1 else ""),
                            set_name, {"stretch_fraction": f}))
    for dd in DIAMETER_OFFSETS:
        devs.append(lattice(f"{set_name}_dd{'m' if dd < 0 else 'p'}{abs(dd)}", d0 + dd, a0, s0,
                            f"diameter {dd:+d} nm at fixed centres", set_name, {"stretch_fraction": 1.0}))
    for dv in (-DV, DV):
        v = v0 + dv
        devs.append(lattice(f"{set_name}_v{v:.3f}".replace(".", "p"), d0, d0 * v, s0,
                            f"overlap v {dv:+.2f}", set_name, {"stretch_fraction": 1.0}))
    return devs


def overlap_series():
    """2024 molecule overlap series + 50 x 50 um mesa, copied verbatim (translated only)."""
    rects = read_pat(os.path.join(HERE, "inputs", "other_patterns_kpz_tb_2024.pat"), expand=False)["overlap_series"]
    rects = rects - np.array([rects[:, 0].min(), rects[:, 1].min()] * 2)
    return {"name": "overlap_series_2024", "structures": [("", rects, None)],
            "params": {"variation": "2024 KPZ field overlap_series: dimers d 1.8 / 2.1 um, v 0.4-1.3, "
                                    "plus 50 x 50 um planar mesa"}}


HEADER = [
    "Etch and overgrow 2026, stretched honeycomb (Kekule) lattices, pump-blueshift edge states",
    "generated by pattern_creator/projects/eno_run_2026/stretched_honeycomb.py",
    "target etch depth 18 meV; GPE sets #1 (17.50 meV) and #3 (18.80 meV) from gpe_v3.py",
    "per set: stretch 0/50/80/100/120 % of s_opt, diameter -80/-40/+40 nm, overlap v -+0.03",
    "units nm; exposed area = pillar mesas; lattices on 10 nm raster, I 16, C 100 (as 2024 EnO lattices)",
    "lattices: generate_pattern.Lattice (bulk _x_0_y_0 with D-line repetition + edge/corner structures),",
    "trimmed so that no area is exposed twice; parameters in shc_field_devices.csv",
]


if __name__ == "__main__":
    out = os.path.join(HERE, "ecp_layout", "stretched_honeycomb")
    groups = [(SYSTEM, set_devices("set3")), (SYSTEM, set_devices("set1")), ("ref", [overlap_series()])]
    fields, height_nm = T.pack_compact(groups)
    if len(fields) != 1:
        raise RuntimeError("layout must fit into one write field (one stage operation per chip)")
    info = T.write_chip(out, CHIP, fields, HEADER)
    shutil.copy(os.path.join(HERE, "inputs", "numbers_xy.pat"), os.path.join(out, "numbers_xy.pat"))
    pitch_x = int(np.ceil((info["width_um"] + STREET_UM) / 10) * 10)
    pitch_y = int(np.ceil((height_nm / 1000 + STREET_UM) / 10) * 10)
    nx, ny = min(REGION_UM // pitch_x, 98), min(REGION_UM // pitch_y, 98)
    T.numbers_ctl(os.path.join(out, "shc_numbers.ctl"), "stretched honeycomb region", nx, ny, pitch_x, pitch_y)
    T.region_jdf(os.path.join(out, "shc_region.jdf"), CHIP, "shc_numbers", nx, ny, pitch_x, pitch_y)
    print(f"{CHIP}: {len(info['devices'])} devices in one write field, chip {info['width_um']:.0f} x "
          f"{height_nm / 1000:.0f} um, placeholder array {nx} x {ny} at {pitch_x} x {pitch_y} um")
    for r in info["devices"]:
        print(f"  {r['label']:>3} {r['structure']:<34} {r['width_um']:5.1f} x {r['height_um']:5.1f} um  "
              f"cells {r.get('supercells', ''):>5}  d {r.get('d_nm', ''):>8} a {r.get('a_nm', ''):>8} "
              f"s {r.get('s_nm', ''):>7} gap {r.get('inter_gap_nm', ''):>6}")

