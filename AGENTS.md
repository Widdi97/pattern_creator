# AGENTS.md — pattern_creator

Instructions for AI agents (and humans) who generate e-beam patterns with this
repository for the XENOS ECP pattern generator at TEP. Read this before touching
any pattern. A complete worked example is `projects/eno_run_2026/` (stretched
honeycomb lattices, Oct 2026); its `README.md` lists the concrete commands.

## Environment

- Python: `C:\ProgramData\anaconda3\python.exe` (base env). `python`/`git` are not on PATH.
- Always `set MPLBACKEND=Agg` (PowerShell: `$env:MPLBACKEND="Agg"`): several modules plot.
- GDS export needs `pip install -r requirements-gds.txt` (gdstk, klayout); see `GDS_EXPORT.md`.
- ECP: `C:\Users\siw60xm\Documents\Promotion\ECP\ECP_2025\ecp.exe` (current),
  manual `...\ECP\ECP\ECP Manual.pdf` (2006, still valid for the file formats).
- `tep_polariton_gpe_code` imports this repo (`generate_pattern.Pattern/Lattice/circle`)
  to build simulation potentials: any change here changes simulations. Keep library
  changes bit-identical in output, and prove it (see "raycasting" below).

## The physics rule

Never invent geometry. Every diameter, overlap and stretch must come from the user or
from the GPE simulation files of the project, and the pattern must be built with the
same construction as the simulation (same `generate_pattern.Lattice`, same basis).
One wafer has one etch depth (= one confinement potential): do not mix parameter sets
optimised for different depths. Ask when unsure.

## ECP file formats (what actually works on our tool)

- `.pat` structures: `D name[, px, py, nx, ny]` / `I increment` / `C dwell_ns` /
  shapes / `END`. Coordinates are **integer nm** in the write field, origin bottom-left,
  usable range 0..500 000 nm (500 um field). The optional D-line suffix repeats the whole
  structure nx x ny times with integer periods px, py (used for lattice bulk).
  Shapes in use: `RECT x1, y1, x2, y2` (x1<x2, y1<y2) and `P 0, x1, y1, x2, y2`
  (numeric code for RECT, used by the 2024 number glyphs). Comment lines start with `;`.
  Names: letters, digits, `-`, `_`.
- `.ctl`: `current = 25000`, `origin = 0, 0`, `sfile = <pat without extension>`,
  `x = ..`, `y = ..`, `+x = ..` (um), `stage`, `draw(name)`, `idraw(prefix, loopvar)`,
  `for n = 1 to N` / `next n`. **The last line must be `END`** (manual 5.2.13; the 2024
  numbers ctl lacked it). All pat files must be in the ctl's directory.
- `.jdf` / `.sdf`: JEOL job files. `ARRAY (x0, nx, pitch_x) / (y0, ny, pitch_y)` repeats a
  `.v30` (um). RESIST/SHOT/STDCUR/CALPRM values in our templates are copied from the
  2024 EnO run — confirm them at the tool.
- `.v30` (JEOL pattern data) is produced by ECP: open the ctl, **File -> Export -> JEOL**.
- **Dose on the JEOL = shot ranks.** A .v30 stores dose only as an area shot-time rank
  (`FF05 ST` before groups of figures, JEOL52 V3.0 spec section 4.3, max rank 63, little-endian
  words). ECP's export turns every distinct dwell time (pat `C` lines and `draw(name, I, C)`
  overrides) into one rank, ascending; the jdf then needs `RESIST` = dose of the shortest dwell
  (= current x dwell / (I x 1 nm)^2, truncated) and `SHOTnn: MODULAT ((rank, %), ...)` with
  % = (dwell/dwell_min - 1) x 100, truncated. Verified against all 2024 jobs (HC_TOPO: dwells
  60/70/80/100/122 ns -> RESIST 585, MODULAT 0/16/33/66/103). `eno_tools.dose_ranks` /
  `job_jdf` implement this; ECP's own exported jdf must agree. Dose classes (e.g. proximity
  correction) are therefore written as different `C` values, never by editing the .v30.
  The ECP_2025 "Proxy" dialog (double Gaussian alpha/beta/eta) did not work for us (Oct 2026).
- 2024/2026 EnO conventions: exposed area = pillar mesas; lattices `I 16`, `C 100`,
  25 nm raster; field x/y labels from `numbers_xy.pat` (glyphs at x 20-52 um, y 0-60 um,
  `nbr_x_0..98`, `nbr_y_0..98`). 2024 used a separate numbers ctl + jdf ARRAY; since 2026
  one grid ctl (`eno_tools.grid_ctl`) draws field + labels at every grid position
  (`for` loops, one `stage` per field) and the jdf places that single `.v30` once.

## Workflow (proven Oct 2026)

1. Generator script per project (flat, parameter block at the top, docstring stating the
   GPE source file/lines of every parameter). Build devices with
   `projects/eno_run_2026/eno_tools.py`: `lattice_structures` (wraps `generate_pattern.Lattice`),
   `shapes_to_rects` (any shapes), `write_chip` (pat + ctl + device CSV + previews).
2. Put everything into **one 500 um write field** (every `stage` costs time; see `TODO.md`).
   Place devices explicitly (fixed grid like the 2024 KPZ field) or with `pack_chip`.
3. Checks (all in `projects/eno_run_2026/`), run after every change:
   - `check_pat.py <pat>`: exact double-exposure check on integer coordinates
     (repetition-aware) + pillar count / diameter per device.
   - `check_with_numbers.py <chip.pat> <numbers.pat>`: same, chip + number glyphs.
   - `verify_layout.py <dir>`: pillars vs. the GPE construction, ctl/pat/jdf consistency.
4. Look at the previews (`*_preview.png`), then open the grid ctl in ECP with few copies
   (e.g. 3 x 2; large loops make ECP unresponsive) and check field + labels.
5. Export `.v30` in ECP (File -> Export -> JEOL) from the grid ctl, then verify it:
   `compare_v30.py <file.v30> <grid.ctl>` decodes the JEOL52 file (`read_v30.py`) and compares
   every rectangle and shot rank with the ctl/pat (Oct 2026: 6.39 M rectangles identical).
   Check ECP's exported jdf against `job_jdf` (RESIST, MODULAT) before writing.
6. KLayout/GDS: `make_gds.py <dir>` (verified cell library from the pat files via
   `pattern_creator_export`, plus assembled top cells; checks merged area == pat area).

## Caveats (all hit in practice)

- **`generate_pattern.Lattice` integer periods.** The D-line repetition uses `int(A)`
  while each cell raster spans the exact `A`. Result: up to 1 nm double-exposed slivers
  between cells, and the top/right edge structures sit `n_cells * (A - int(A))` (up to
  ~10 nm) away from the bulk. `eno_tools.lattice_structures` moves those edges back and
  trims overlaps (`make_exposure_unique`); do not use `Lattice.pat_str` directly for
  non-integer lattice constants. Its corner structures are placed with an extra `+A_y`
  offset in `generate_patterns`; in our lattices the corners were empty — if yours are
  not, check them visually. Empty edge/corner structures are dropped (do not write
  empty `D` blocks).
- **Raster vs. small gaps.** Shapes are rasterised at pixel centres. Gaps below ~2 raster
  steps render inconsistently (some bonds merge, others not). Check pillar counts
  (`check_pat.py`) and use a finer raster for such devices, or accept merging consciously.
- **Overlapping shapes** are fine inside one raster (union), but two structures must never
  cover the same area. Coarse painting-based checks can be fooled when repetition periods
  are not multiples of the pixel: use the exact checker.
- **`Pattern` caches.** If you write `pattern.pattern` directly, set
  `pattern.pat_file_string_updated = False` before `export_pattern`.
- **raycasting speed.** `Pattern.add_parametrized_shape` now uses the numba kernel
  `raycasting.points_in_closed_curve_rows` (~90x faster). It was verified bit-identical
  to the old per-row `points_in_closed_curve` (300 random shapes + full lattices). Re-run
  such an identity test if you touch it — the GPE potentials depend on it.
- **Overlap convention.** In the blueshift/Kekule GPE code `v = a / d` with `a = 2 r v`,
  `a_latt = 3 a`, pillars at `a + s`; other projects use other conventions (v = a/d_mean,
  v = a/d_small). Always copy the formula from the simulation file.
- **Write-field fit.** 4 x 4 lattices of ~90 um plus references just fit 500 um; Lattice
  rounds `x_size, y_size` down to whole unit cells, so actual sizes vary by a few um.
- **ECP GUI automation.** Do not drive the real mouse/keyboard while the user works
  (focus is stolen, clicks land in other apps). Windows UI Automation reaches ECP's
  toolbar and dialogs, but Qt menu popups are not exposed; ask the user to click menus
  (File -> Open, File -> Export -> JEOL) and give them the exact file path.
- **Numbers/arrows placement.** `numbers_xy.pat` glyph positions are fixed; to move them,
  write a shifted copy (see `shifted_numbers` in `stretched_honeycomb.py`) instead of
  extra stage moves.
- **ECP_2025 JEOL export** (Oct 2026): profile "JBX 8100 FS", 1000 um JEOL field; our
  500 um pattern field is placed with a 250 um position-set offset (centred). D-line
  repetition becomes data-compaction mode 8 (`FFE8`), whose Lx/Ly are the start-to-end
  lengths (= (N-1) x pitch), not the pitch. Its jdf wrote `MODULAT ((0, 0), (1, 121.00))` for
  dwells 100/122 ns, while the 2024 exports (and the rule above) give 22 %: check which
  convention the tool expects before relying on ranks. It also writes its own JOB/EOS/RESTYP/
  SHOT/STDCUR lines (e.g. `SHOT A, 10`, `STDCUR 25.00`) that differ from the 2024 jobs.
- **GDS export** (`pattern_creator_export.pat.export_pat`) writes a library of independent
  cells (stage/ctl assembly is not applied) and renames long/unsafe names (report gives the
  alias). Assemble top cells with `klayout.db` as in `make_gds.py`.
