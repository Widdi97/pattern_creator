"""KLayout/GDS file of the stretched-honeycomb layout.

Uses pattern_creator_export (GDS_EXPORT.md): every structure of shc_field.pat and
numbers_shc.pat becomes a verified GDS cell (exact PAT rectangles, D-line
repetition kept as cell arrays, 1 nm grid, layer 1/0). On top of that library this
script adds assembled top cells with klayout.db:
    SHC_FIELD           one 500 um write field (the structures drawn per grid position)
    SHC_GRID_<nx>X<ny>  the field grid with its x/y index labels, exactly as shc_grid.ctl
and checks that the flattened field area equals the summed PAT rectangle area
(no double exposure, nothing lost).

usage: python make_gds.py <layout_dir>
"""
import os
import re
import sys
from pathlib import Path

import klayout.db as kdb
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from pattern_creator_export.pat import export_pat, parse_pat  # noqa: E402

from check_pat import read_pat  # noqa: E402

if __name__ == "__main__":
    layout_dir = Path(sys.argv[1])
    ctl = (layout_dir / "shc_grid.ctl").read_text()
    draws = re.findall(r"^draw\((\S+)\)", ctl, flags=re.M)
    sfiles = re.findall(r"^sfile = (\S+)", ctl, flags=re.M)
    nx = int(re.search(r"for n = 1 to (\d+)", ctl).group(1))
    ny = int(re.search(r"for m = 1 to (\d+)", ctl).group(1))
    pitch_x = int(re.search(r"\+x = (\d+)", ctl).group(1))
    pitch_y = int(re.search(r"\+y = (\d+)", ctl).group(1))
    field_pat = layout_dir / f"{sfiles[0]}.pat"
    numbers_pat = layout_dir / f"{sfiles[1]}.pat"
    out = layout_dir / "shc_field.gds"
    library = out.with_name("shc_field_cells.gds")

    defs = parse_pat(field_pat.read_text(encoding="utf-8")) + parse_pat(numbers_pat.read_text(encoding="utf-8"))
    report = export_pat(defs, library)
    alias = {c["source_name"]: c["gds_cell"] for c in report["cells"]}
    print(f"cell library: {len(report['cells'])} PAT structures, KLayout validation {report['validation']}")

    ly = kdb.Layout()
    ly.read(str(library))
    dbu = ly.dbu  # um per database unit (0.001)
    field = ly.create_cell("SHC_FIELD")
    for name in draws:
        field.insert(kdb.CellInstArray(ly.cell(alias[name]).cell_index(), kdb.Trans()))

    grid = ly.create_cell(f"SHC_GRID_{nx}X{ny}")
    for j in range(ny):
        for i in range(nx):
            t = kdb.Trans(int(round(i * pitch_x / dbu)), int(round(j * pitch_y / dbu)))
            grid.insert(kdb.CellInstArray(field.cell_index(), t))
            for label in (f"nbr_x_{i + 1}", f"nbr_y_{j + 1}"):
                grid.insert(kdb.CellInstArray(ly.cell(alias[label]).cell_index(), t))

    # check: flattened field area (merged) == sum of PAT rect areas (expanded)
    pat = read_pat(str(field_pat))
    pat_area = sum(float(np.sum((r[:, 2] - r[:, 0]) * (r[:, 3] - r[:, 1]))) for n, r in pat.items() if n in draws)
    merged = kdb.Region(field.begin_shapes_rec(ly.layer(1, 0))).merged()
    gds_area = merged.area() * (dbu * 1000) ** 2  # nm^2
    print(f"field area: PAT rect sum {pat_area / 1e6:.3f} um^2, merged GDS {gds_area / 1e6:.3f} um^2, "
          f"difference {abs(gds_area - pat_area):.0f} nm^2")
    if abs(gds_area - pat_area) > 0:
        raise RuntimeError("merged GDS area differs from PAT area: overlap or lost geometry")
    ly.write(str(out))
    library.unlink()
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB); top cells SHC_FIELD, {grid.name} "
          f"({nx} x {ny} at {pitch_x} x {pitch_y} um)")
