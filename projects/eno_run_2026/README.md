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

## Other EnO 2026 systems

BBH, pi-flux diamond chain, monotile TI, anisotropic KPZ, Lieb altermagnet, SLM Berry
honeycomb and vortex waveguides were analysed (Oct 2026) but are on hold by user decision.
