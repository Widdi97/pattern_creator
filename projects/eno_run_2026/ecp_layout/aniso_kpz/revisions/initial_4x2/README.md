# Anisotropic KPZ: separate A, B and C layouts

Each `set_a`, `set_b` and `set_c` has its own `.gds`, `.pat`, `.ctl`, device
table, preview and validation report. Each contains eight devices in one
500 x 500 um field, written once. Numbers 1-4 run left to right in the upper
row; 5-8 run left to right below. The prefix A/B/C is given by the file name.
GDS top cells are `KPZ_SET_A`, `KPZ_SET_B`, `KPZ_SET_C`; geometry is layer 1/0,
with 1 nm database units. Previews render the saved GDS.

Native `.v30` files are **pending ECP export**; none has been substituted or
renamed from another format. `manifest.json` records this explicitly.

## Geometry and exposure conventions

- Source: the supplied `lattice_sets_results.txt`, full-precision records at
  lines 286-929. Its path and SHA256 are in `geometry_catalog.json`.
- All three sets are retained separately, including their shared designs:
  24 devices from 20 unique geometries. Radii are semiaxes, angles are CCW.
- Finite patches contain whole mesas with their original rounded exterior
  caps. For each axis, `N = floor((90000 - 2*halfwidth)/pitch) + 1`; both
  dimensions fit within approximately 90 um. This finite termination is a
  layout choice: the source describes infinite lattices.
- Each lattice has nine separately named components: `bulk`, `left`, `right`,
  `bottom`, `top`, `bl`, `br`, `tl`, `tr`. Midplanes partition the union without
  duplicate exposure; bulk and edges use PAT/GDS repetitions.
- The simulation uses implicit ellipses. `geometry.py` evaluates the same
  ellipse union directly on cell centres, then produces non-overlapping
  integer-nm rectangle strips. It does not reconstruct legacy shape history.
- The maximum geometry raster step is 5 nm, finer than the neighboring
  honeycomb layout: B4 and A7 have nominal gaps of 10.03 and 12.82 nm. Both
  retain a 10 nm written gap. GDS and PAT contain the same raster geometry.
- Confirmed EnO settings: exposed area = pillar mesas, current 25000 pA,
  `I 16`, `C 100 ns`; one field copy. Geometry raster and exposure increment
  are distinct. These inherited settings are not a new process calibration.
- The source calculations use 20 meV confinement, whereas the neighboring
  honeycomb study used 18 meV. No physical etch height is inferred or retuned.

## Regenerate and verify

Use the existing pattern_creator Python environment (NumPy, Matplotlib etc.)
plus the optional dependencies in the repository's `requirements-gds.txt`:
`gdstk==1.0.1`, `klayout==0.30.10`. No other dependencies are added.

```powershell
$env:MPLBACKEND = 'Agg'
& C:\ProgramData\anaconda3\python.exe -B -m unittest test_geometry test_v30 -v
& C:\ProgramData\anaconda3\python.exe -B generate_layout.py <path-to-lattice_sets_results.txt> --output regenerated
```

Choose a fresh output directory: regeneration refuses to overwrite an existing
layout. The generator checks 20 unique input records and all 24 memberships,
field bounds, nine components per device, source connectivity, exact PAT/GDS
area equality without overlaps, and zero XOR after final GDS readback. The
tests separately check finite unions, rotations, borders and the narrow gaps.
Existing pattern_creator library code is unchanged.

## Native V30 export

Local ECP: `C:\Users\jod52fr\Documents\Doktorarbeit\Prozess\ecp\ecp.exe`.
Open each `.ctl` separately and use **File -> Export -> JEOL** to save
`set_a.v30`, `set_b.v30`, `set_c.v30` beside their PAT/CTL files. The existing
2026 export convention is JBX 8100 FS, 1000 um JEOL field, 125 MHz; the ECP
layout field is 500 um / 500000 pixels. Keep ECP's accompanying JDF/SDF files.

The strict checker expects the 500 um pattern centred in that JEOL field
with position set `(250000,250000)` nm, one field at `(0,0)`, 1 nm units and
rank 0. It checks a fixed coordinate transform, not a fitted bbox alignment.

```powershell
& C:\ProgramData\anaconda3\python.exe -B verify_v30.py set_a.v30 --pat set_a.pat
& C:\ProgramData\anaconda3\python.exe -B verify_v30.py set_b.v30 --pat set_b.pat
& C:\ProgramData\anaconda3\python.exe -B verify_v30.py set_c.v30 --pat set_c.pat
```

`verify_v30.py` uses only the Python standard library and rejects unsupported
or truncated records, wrong ranks/counts/placement and missing/duplicate
rectangles. Successful checks print JSON with the file hashes. Geometry
agreement does not qualify the JDF settings or the exposure process.
