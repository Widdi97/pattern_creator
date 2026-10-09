# TODO

## Minimise e-beam stage operations in ECP control files (2026-10-09)

Every `x = ...` / `y = ...` / `+x = ...` followed by `stage` in a `.ctl` file triggers an
e-beam stage operation, and each stage operation takes a lot of time. Therefore the
positions of the individual devices should be optimised **inside the e-beam write field**
defined in the `.pat` files: place the devices at different coordinates within the
patterns (absolute nm offsets in the RECT coordinates of each structure) instead of
moving the stage between devices. This is the most efficient way to write a chip.

- Reference: `projects/etch_and_overgrow_kpz/pattern_generation_kzp_tb` (`global_offsetx/y`
  of `Lattice` place all lattices on a 130 um grid inside one field;
  compare `pat_string_1_stage_operation.pat` vs `pat_string_2_stage_operations.pat`).
- Already applied in `projects/eno_run_2026` (`eno_tools.pack_chip` packs all devices into
  the 500 um write field; a chip that fits one field needs one stage operation).
- Open: the per-chip numbering ctl (`numbers_*.ctl`) still issues one stage operation per
  chip in its `for` loops, on top of the jdf ARRAY moves.
