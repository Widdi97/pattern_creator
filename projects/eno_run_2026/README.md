# EnO run 2026 — e-beam patterns

Etch-and-overgrow sample (Oct 2026). Physics source:
`tep_polariton_gpe_code/projects/full_ab_initio/EnO_run_2026/`. General workflow and
caveats: `../../AGENTS.md`.

## Stretched honeycomb (Kekule) lattices — pump-blueshift edge states

Source: `.../adiabatic_topology_blueshift/gpe_v3.py`, `gpe_v3_optimise.py`.
Decisions (user, 2026-10-09):

- one etch depth for the whole wafer, target **18 meV** confinement;
- pillar diameter **2050 nm** for all lattices (between the GPE optima: set #1
  d 2019 nm at 17.5 meV, set #3 d 2071 nm at 18.8 meV);
- **4 x 4 grid**: columns overlap `v = a/d` = 1.100 / 1.133 / 1.167 / 1.200, rows stretch
  `s` = 0 / 80 / 110 / 140 nm (s = 0 is the plain honeycomb reference);
- lattices ~90 x 90 um, built with `generate_pattern.Lattice` exactly like the GPE
  potential (`a = d v`, `a_latt = 3a`, six pillars at `a + s`);
- 25 nm raster, `I 16`, `C 100`, exposed area = pillar mesas;
- one 500 um write field per chip (one stage operation): left column 2024 overlap-series
  dimers (17), 2024 50 x 50 um mesa (18), chip x/y numbers with the 2024 arrows; lattices
  1-16 to the right (row = stretch, top row s = 0; column = v);
- one ctl (`shc_grid.ctl`) writes the field grid with the field x/y index labels; the
  number of copies (`GRID_NX`, `GRID_NY`, pitch 550 um) is set by the user.

Lattices 9, 13, 14 (v 1.100 / s 110, v 1.100 / s 140, v 1.133 / s 140) have a negative
inter-hexamer gap: their short-bond pillar pairs merge (exposed once, union).

### Regenerate and verify

```
$env:MPLBACKEND="Agg"
cd C:\Users\siw60xm\Documents\Promotion\Code\pattern_creator\projects\eno_run_2026
C:\ProgramData\anaconda3\python.exe stretched_honeycomb.py
C:\ProgramData\anaconda3\python.exe check_pat.py ecp_layout\stretched_honeycomb\shc_field.pat 25
C:\ProgramData\anaconda3\python.exe check_with_numbers.py ecp_layout\stretched_honeycomb\shc_field.pat ecp_layout\stretched_honeycomb\numbers_shc.pat
C:\ProgramData\anaconda3\python.exe verify_layout.py ecp_layout\stretched_honeycomb
C:\ProgramData\anaconda3\python.exe make_gds.py ecp_layout\stretched_honeycomb
```

After the ECP export (File -> Export -> JEOL of `ecp_test\shc_grid.ctl`):

```
C:\ProgramData\anaconda3\python.exe compare_v30.py ecp_layout\stretched_honeycomb\ecp_test\shc_grid.v30 ecp_layout\stretched_honeycomb\ecp_test\shc_grid.ctl
```

Build ~15 s. Last results: no double exposure (field, field + numbers, merged GDS area ==
PAT area); all pillars on the GPE lattice sites within 4.3 nm; d_eq 2049-2050 nm.

### Files in `ecp_layout/stretched_honeycomb/`

| File | Purpose |
|---|---|
| `shc_grid.ctl` | the only ctl: `GRID_NX x GRID_NY` fields (default 3 x 2, set in the script), each with its x/y index labels -> export `shc_grid.v30` |
| `shc_field.pat` | all structures of one field (absolute coordinates in the 500 um field) |
| `numbers_shc.pat` | field x/y index labels (2024 glyphs, shifted into the left column) |
| `shc_grid.jdf` / `.sdf` | job placing `shc_grid.v30` once (RESIST etc. copied from 2024, check at the tool) |
| `shc_field_devices.csv` | per lattice: d, v, a, s, gaps, unit cells, pump-target hexamer centre |
| `shc_field.gds` | KLayout: cells of all structures + `SHC_FIELD` and `SHC_GRID_<nx>X<ny>` (= shc_grid.ctl) |
| `*_preview.png`, `*_log.txt` | previews and check logs |
| `ecp_test/` | copy of the files for opening in ECP |

### Other files

- `eno_tools.py` — rasteriser, Lattice wrapper with seam/overlap fixes, pat/ctl/jdf writers,
  shot-rank rule (`dose_ranks`).
- `read_v30.py` / `compare_v30.py` — JEOL52 V3.0 reader and rectangle-exact check of an ECP
  export against the ctl/pat.
- `inputs/numbers_xy.pat`, `inputs/other_patterns_kpz_tb_2024.pat` — 2024 numbers, arrows,
  overlap series (used verbatim, translated only).

## Vortex waveguides — single-shot space-time vortices (3-QW wafer)

Source: `tep_polariton_gpe_code/projects/time_dependent/waveguide_space_time_vortices/`
(`04_layout_width_depth_scan.py`, results `04_width_depth_scan_20261013_212543`; checks `05`, `06`).
Inputs: E_X 1.4707 eV, Rabi 4.2 meV (user 2026-10-13: 3 InGaAs QWs), m_c 3.2e-5 m_e, m_X 0.2 m_e,
mesa detuning -1.886 Rabi = -7.92 meV (user 2026-10-12). Separate wafer from the Semenoff lattices
(user 2026-10-13), so it has its own etch depth.

- design depth **18 meV** photon confinement: the gap from the transverse ground mode to the next
  state saturates with depth (exciton-limited LP trap); 18 meV is within 1-2 % of 22 meV;
- the gap peaks at W* = 1.6 um (-7.92 meV), 1.5 um (-2 Rabi), 1.2 um (-3 Rabi) at 18 meV;
  4.72 meV at 1.6 um vs 4.23 meV at 2 um and 2.52 meV at 3 um;
- guides >= 250 um long (user 2026-10-13: "make the waveguides at least 250um long in the layout as in
  the experiment we have observed self interference upon reflection at the wg end");
- field: one top-aligned row, widths 1.0 / 1.2 / 1.4 / 1.6 / 1.8 / 2.0 / 3.0 um, per width one guide of
  250 / 350 / 450 um (450 um = longest that fits with its label), 19 um pitch, guide axis y, one exact
  RECT per guide (exposed = mesa = guide stripe), `I 16`, `C 100`; left column as the honeycomb field
  (2024 overlap dimers, 2024 50 um mesa, chip numbers + arrows). Series, lengths per width and pitch
  are a proposal to be confirmed.

```
$env:MPLBACKEND="Agg"
C:\ProgramData\anaconda3\python.exe vortex_waveguides.py
C:\ProgramData\anaconda3\python.exe check_pat.py ecp_layout\vortex_waveguides\vwg_field.pat 25
C:\ProgramData\anaconda3\python.exe check_with_numbers.py ecp_layout\vortex_waveguides\vwg_field.pat ecp_layout\vortex_waveguides\numbers_vwg.pat
C:\ProgramData\anaconda3\python.exe verify_waveguides.py ecp_layout\vortex_waveguides
C:\ProgramData\anaconda3\python.exe make_gds.py ecp_layout\vortex_waveguides vwg_grid.ctl
```

After the ECP export (File -> Export -> JEOL of `ecp_test\vwg_grid.ctl`):
`compare_v30.py ecp_layout\vortex_waveguides\ecp_test\vwg_grid.v30 ecp_layout\vortex_waveguides\ecp_test\vwg_grid.ctl`.
Last results (2026-10-13): 21 guides, all exact W x L rects at the CSV centres, smallest etched gap
16 um; no double exposure (field, field + numbers, merged GDS area == PAT area).
Files in `ecp_layout/vortex_waveguides/` mirror the honeycomb ones (`vwg_grid.ctl`, `vwg_field.pat`,
`numbers_vwg.pat`, `vwg_grid.jdf/.sdf`, `vwg_field_devices.csv`, `vwg_field.gds` with top cells
`VWG_FIELD`, `VWG_GRID_<nx>X<ny>`, previews, logs, `ecp_test/`).

## Semenoff (staggered honeycomb) lattices — detection-SLM Berry curvature (3-QW wafer)

Source: `tep_polariton_gpe_code/projects/full_ab_initio/EnO_run_2026/flex_fund_slm_berry_curvature/`
(`model_definitions.py` geometry, `06_final_design.py` -> `results/04_final_design.json`, report in `report/`).
Separate wafer from the stretched honeycomb and from the low-top-mirror waveguides (user 2026-10-13).

- one etch depth, target **15.5 meV**; mean diameter **d̄ = 1800 nm** for all lattices;
- **4 x 4 grid** (user: "η_d × v"): rows staggering η_d = (d_A − d_B)/d̄ = 0 / 0.15 / 0.22 / 0.29 (top row = plain
  honeycomb), columns v = a/d̄ = 0.90 / 0.95 / 0.98 / 1.05, a = A–B centre distance; recommended lattice η 0.29, v 0.95
  (d_A 2061 nm, d_B 1539 nm, a 1710 nm). v within ±0.015 of 1 is refused (gaps of a few raster steps);
- lattices ~90 x 90 um, built with `generate_pattern.Lattice` like the GPE construction: a1 = √3 a (1, 0),
  a2 = √3 a (1/2, √3/2), circle d_A at (0, 0), circle d_B at (0, a); `lattice_structures(..., fix_corner_offset=True)`
  because the corners carry pillar parts here; v < 1 lattices are one merged network, except that at
  v = 0.98 the 30 truncated pillars of the bottom edge row are detached (36 nm overlap, Lattice boundary cut);
- 25 nm raster, `I 16`, `C 100`, field arrangement, references (2024 dimers + mesa, verbatim) and numbers as stretched honey.

### Regenerate and verify

```
$env:MPLBACKEND="Agg"
cd C:\Users\siw60xm\Documents\Promotion\Code\pattern_creator\projects\eno_run_2026
C:\ProgramData\anaconda3\python.exe semenoff_lattice.py
C:\ProgramData\anaconda3\python.exe check_pat.py ecp_layout\semenoff_slm\sem_field.pat 25
C:\ProgramData\anaconda3\python.exe check_with_numbers.py ecp_layout\semenoff_slm\sem_field.pat ecp_layout\semenoff_slm\numbers_sem.pat
C:\ProgramData\anaconda3\python.exe verify_semenoff.py ecp_layout\semenoff_slm
C:\ProgramData\anaconda3\python.exe make_gds.py ecp_layout\semenoff_slm sem_grid.ctl
```

`semenoff_lattice.py` reads the grid from the GPE project's `results/04_final_design.json` (override:
`SEMENOFF_DESIGN_JSON`, output dir `SEMENOFF_LAYOUT_OUT`). `verify_semenoff.py` compares the written pattern with the
analytic union of disks (FFT-aligned window of 3 x 3 cells; works for merged pillars): area XOR, per-sublattice
equivalent diameter in the power-diagram cells and centroid. Last results: no double exposure (field, field +
numbers, merged GDS area == PAT area), XOR ~1 % (raster edge), diameters within 3.6 nm, centroids within 4.2 nm.
After the ECP export (File -> Export -> JEOL of `ecp_test\sem_grid.ctl`) check it with `compare_v30.py` as above.

### Mass domain walls (valley-Hall transport) — second write field `semw_field`

User 2026-10-14: "semenoff transport interfaces where the mass changes sign ... Design both". `semenoff_walls.py`
builds one 500 um field with 8 lattices (~91 x 91 um, 2136 whole pillars each, wall along x through the middle):
rows η_d = 0.29 (recommended bulk lattice) / 0.22, columns chain LL, chain SS, dimer LL, dimer SS, all at d̄ 1800 nm,
v 0.95, 15.5 meV. Below the wall A is large, above B is large (or the reverse, chosen so that the wall pillars are
all large = LL or all small = SS; the script refuses a mixed wall). Families as in the GPE ribbon
(`07_domain_wall_ribbons.py`): *chain* = the wall cuts the 30° bonds, the wall pillars form a zigzag chain of equal
size; *dimer* = the wall cuts the vertical bonds, equal-size dimers across the wall. The pillars are written as
explicit disks (`shapes`, union rasterised exactly, no D-line repetition) with the same site construction as the GPE
supercell; `semw_sites.npz` holds that list per lattice (x, y, d, big, sublattice, above-wall; nm, field coordinates)
and `semw_field_devices.csv` the wall line. At η 0.29 the small-small bonds of the SS walls have an etched gap of
171 nm (the two domains are separate networks, 2 components in the check); the LL walls overlap by 351 nm.

```
C:\ProgramData\anaconda3\python.exe semenoff_walls.py
C:\ProgramData\anaconda3\python.exe check_pat.py ecp_layout\semenoff_walls\semw_field.pat 25
C:\ProgramData\anaconda3\python.exe verify_semenoff_walls.py ecp_layout\semenoff_walls
C:\ProgramData\anaconda3\python.exe make_gds.py ecp_layout\semenoff_walls semw_grid.ctl
```

`verify_semenoff_walls.py` paints a 14 x 14 um window around each wall from the pat and compares it with the analytic
disk union (XOR) and, per pillar class (large/small x wall/bulk), the power-cell equivalent diameter. Last results
(2026-10-14): no double exposure (field; numbers bbox exact test), XOR ~1 % (raster edge), all classes within 2.9 nm,
merged GDS area == PAT area. The field-numbers overlap test of `check_with_numbers.py` is O(n^2) on the explicit
disks and too slow here; `verify_semenoff_walls.py` does an exact bounding-box test of the numbers instead.

## Other EnO 2026 systems

BBH, pi-flux diamond chain, monotile TI, anisotropic KPZ, Lieb altermagnet and SLM Berry
honeycomb were analysed (Oct 2026) but are on hold by user decision (vortex waveguides: see above).
