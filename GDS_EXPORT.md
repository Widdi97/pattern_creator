# GDS export

The optional `pattern_creator_export` package adds GDS export without changing
`generate_pattern.py`, existing imports, or `.pat` output.

## Additional dependencies

Use Python 3.10 or newer in your existing Pattern Creator environment:

```sh
python -m pip install -r requirements-gds.txt
```

- `gdstk==1.0.1` creates GDS polygons, Boolean geometry and cell arrays.
- `klayout==0.30.10` independently checks PAT exports and runs geometry tests.
- NumPy is also used; it is already needed by Pattern Creator and is a gdstk
  dependency. Existing Matplotlib, Numba and Pillow requirements are unchanged.

Direct export needs gdstk and NumPy. PAT export also needs KLayout because it
checks the written file before publishing it. Legacy generation works without
either new package; importing `pattern_creator_export` alone loads neither.

## Already raycast patterns

Use the existing rectangle export as the geometry source:

```python
from pattern_creator_export.pat import parse_pat, export_pat

# pattern is an existing generate_pattern.Pattern with a completed mask.
definitions = parse_pat(pattern.export_pattern(complete=True))
report = export_pat(definitions, "layout.gds")

# For an existing Lattice, use parse_pat(lattice.pat_str) instead.
```

This preserves the exported raster rectangles, holes, coordinate rounding and
arrays. It does not raycast again or recover smooth curves. Raw NumPy masks
are not accepted directly. If code edits `pattern.pattern` directly, its
legacy rectangle/text caches must be refreshed before calling the old exporter.

Saved files use the same route:

```python
from pathlib import Path
definitions = parse_pat(Path("pattern.pat").read_text(encoding="utf-8"))
report = export_pat(definitions, "pattern.gds")
```

The strict parser supports `D`, `I`, `C`, `RECT`, `P 0`, `CIRCLE`, `XPOLY`,
`YPOLY` and `END`, including structure arrays. Unsupported or malformed input
raises an error. KLayout checks polygon coordinates and references; only a
verified temporary file replaces the destination.
Cell names are normalized to portable GDS identifiers; the report retains the
original name and its GDS alias.

## Direct parametrized geometry

```python
from pattern_creator_export.direct import DirectPattern, DirectLattice, ShapeSpec

pattern = DirectPattern(20000, 20000, 100, pattern_name="RING")
pattern.add_parametrized_shape("circle", 10000, 10000, 5000,
                               boolean_operation="add")
pattern.add_parametrized_shape("circle", 10000, 10000, 4000,
                               boolean_operation="subtract")
metadata = pattern.export_gds("ring.gds", layer=1, datatype=0)

lattice = DirectLattice(
    (2000, 0), (0, 2000), 10000, 8000, 100,
    [ShapeSpec("circle", (0, 0, 500), "add")], [(0, 0)],
    pattern_name="LATTICE",
)
lattice.export_gds("lattice.gds")
```

Direct shapes become polygons without masks or rectangle decomposition.
Supported shapes are `circle(x, y, r)`, `ellipse(x, y, ra, rb, angle_radians)`
and `polygon(x1, y1, ...)`. Pass these as string names. Custom closed-curve
callables require an explicit `samples` count; their sampling error is not
automatically bounded. Add/subtract operations are applied in order. Existing
`Pattern.shapes` omits subtraction history, so it is not safe to replay it.

Every direct lattice has an assembled top plus separate `BULK`, `LEFT`, `RIGHT`,
`TOP`, `BOTTOM`, `CORNER_BL`, `CORNER_BR`, `CORNER_TL` and `CORNER_TR` cells,
including empty components. Direct lattices require `a1` along positive x and
a supported rectangular supercell. They retain the legacy bounded site search
and half-step coordinate shift, but use a common rounded pitch and corrected
corner placement. Those changes apply only to direct GDS; PAT conversion
preserves the saved coordinates. Direct shapes intentionally differ from raster
geometry. Direct export returns geometry metadata; unlike PAT export, it does
not automatically run KLayout on every output.

All API lengths are nanometres; GDS uses micrometre user units and a 1 nm grid.
PAT conversion assumes one source coordinate is 1 nm from the project
convention; it does not infer machine pixel calibration. Curves use a default
1 nm approximation tolerance plus grid rounding. `step_size` still determines
legacy support clipping/offsets, although no mask is allocated. CTL stage
placement, dose and writer-native exposure jobs are not converted.

## Examples and tests

Run from the repository root. Batch output must be a fresh directory outside
the repository; its ledger includes exported and rejected inputs.

```sh
python -m examples.export_gds ../gds_examples
python -m pattern_creator_export.batch_pat . ../gds_batch --export
python -m unittest discover -s tests -p "test_gds_*.py" -v
```

Without `--export`, the batch command only parses and inventories archived
PAT files under `projects` and `examples`. It never executes project scripts.
