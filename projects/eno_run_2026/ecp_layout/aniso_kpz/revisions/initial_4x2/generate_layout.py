"""Build the three anisotropic KPZ fields from the report's explicit geometry.

Run with the repository's optional GDS dependencies and existing Python stack.
The source report is parsed as data; none of its reproduction commands are run.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("MPLBACKEND", "Agg")
import numpy as np
import gdstk
import klayout.db as kdb
import klayout.lay as klay

from geometry import build_device, parse_report

HERE = Path(__file__).resolve().parent
# In the installed location: pattern_creator/projects/eno_run_2026/ecp_layout/aniso_kpz.
ROOT = Path(os.environ.get("PATTERN_CREATOR_ROOT", HERE.parents[3]))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "projects" / "eno_run_2026"))
import eno_tools as T
from pattern_creator_export.pat import export_pat, parse_pat

SIZE_NM = 90_000
MAX_PIXEL_NM = 5  # B4 and A7 have only 10.03 and 12.82 nm transverse gaps.
FIELD_NM = 500_000
CURRENT_PA, INCREMENT, DWELL_NS = 25_000, 16, 100
# Eight devices: four columns, two rows, with room for their numerical labels.
LEFTS_NM = (25_000, 145_000, 265_000, 385_000)
TOPS_NM = (420_000, 250_000)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(path, top_name, output):
    """Render the actual saved GDS, including all cell-array repetitions."""
    view = klay.LayoutView()
    view.load_layout(str(path), False)
    cv = view.active_cellview()
    cv.cell = cv.layout().cell(top_name)
    view.max_hier()
    view.set_config("background-color", "#ffffff")
    view.set_config("grid-visible", "false")
    view.add_missing_layers()
    layers = view.begin_layers()
    while not layers.at_end():
        props = layers.current().dup()
        props.fill_color = props.frame_color = 0
        props.dither_pattern = props.line_style = 0
        view.set_layer_properties(layers, props)
        layers.next()
    # KLayout 0.30.10's monochrome flag can yield a blank image here;
    # explicitly black layers through the normal renderer preserve geometry.
    view.save_image_with_options(str(output), 1500, 1500, 0, 1, 0,
                                 kdb.DBox(0, 0, 500, 500), False)
    view.destroy()


def build_set(letter, records, output):
    stem = f"set_{letter.lower()}"
    selected = []
    for number in range(1, 9):
        label = f"{letter}{number}"
        selected.append((label, next(r for r in records if label in r["memberships"])))
    pat_lines = [f"; Anisotropic KPZ Set {letter}: source geometry in geometry_catalog.json\n",
                 "; nm coordinates; exposed pillar mesas; whole-mesa finite boundaries\n",
                 "; 5 nm maximum geometry raster, I16 C100, one 500 um field\n"]
    devices, names, source_area = [], [], 0
    for index, (label, record) in enumerate(selected):
        dev = build_device(record, size_nm=SIZE_NM, pixel_nm=MAX_PIXEL_NM)
        bbox = np.asarray(dev["written_bbox_nm"], dtype=np.int64)
        dx = LEFTS_NM[index % 4] - bbox[0]
        dy = TOPS_NM[index // 4] - bbox[3]
        shifted = []
        area = 0
        for role, rects, repeat in dev["structures"]:
            name = f"{label}_{role}"
            r = rects + np.array([dx, dy, dx, dy])
            # Arrays preserve the nine roles instead of flattening a whole lattice.
            counts = repeat[2] * repeat[3] if repeat else 1
            area += int(np.sum((r[:, 2] - r[:, 0]) * (r[:, 3] - r[:, 1]))) * counts
            if len(r):
                pat_lines.append(T.structure(name, r, repeat, INCREMENT, DWELL_NS))
                names.append(name)
            shifted.append((name, r, repeat))
        label_name = f"{label}_label"
        lab = T.label_rects(str(index + 1), LEFTS_NM[index % 4],
                            int(bbox[1] + dy - 13_000), height=8_000)
        pat_lines.append(T.structure(label_name, lab, increment=INCREMENT, dwell=DWELL_NS))
        names.append(label_name)
        source_area += area + int(np.sum((lab[:, 2] - lab[:, 0]) * (lab[:, 3] - lab[:, 1])))
        devices.append({"label": label, "record": record, "geometry": dev,
                        "parts": shifted, "area_nm2": area, "offset_nm": (int(dx), int(dy)),
                        "bbox_nm": (bbox + np.array([dx, dy, dx, dy])).tolist()})
    pat_path = output / f"{stem}.pat"
    pat_path.write_text("".join(pat_lines), encoding="ascii")
    ctl = (f"; Anisotropic KPZ Set {letter}; one field, one copy\n"
           f"current = {CURRENT_PA}\norigin = 0, 0\nx = 0\ny = 0\nstage\n"
           f"sfile = {stem}\n" + "".join(f"draw({name})\n" for name in names) + "END\n")
    (output / f"{stem}.ctl").write_text(ctl, encoding="ascii")
    definitions = parse_pat(pat_path.read_text())
    if {d.name for d in definitions} != set(names) or len(names) != len(set(names)):
        raise RuntimeError("CTL must draw every PAT definition exactly once")
    gds_path = output / f"{stem}.gds"
    conversion = export_pat(definitions, gds_path)
    aliases = {c["source_name"]: c["gds_cell"] for c in conversion["cells"]}
    ly = kdb.Layout()
    ly.read(str(gds_path))
    if abs(ly.dbu - .001) > 1e-12:
        raise RuntimeError("GDS database unit must be 1 nm")
    layer = ly.layer(1, 0)
    top = ly.create_cell(f"KPZ_SET_{letter}")
    for dev in devices:
        cell = ly.create_cell(dev["label"])
        for name, r, rep in dev["parts"]:
            if len(r):
                cell.insert(kdb.CellInstArray(ly.cell(aliases[name]).cell_index(), kdb.Trans()))
        region = kdb.Region(cell.begin_shapes_rec(layer)).merged()
        if region.area() != dev["area_nm2"]:
            raise RuntimeError(f"{dev['label']}: overlapping exposure or lost geometry")
        # Whole isolated mesas or rows/columns joined by the specified negative gap.
        rec, geo = dev["record"], dev["geometry"]
        expected = ((1 if rec["signed_axial_gap_x_um"] < 0 else geo["nx"])
                    * (1 if rec["signed_axial_gap_y_um"] < 0 else geo["ny"]))
        if region.count() != expected:
            raise RuntimeError(f"{dev['label']}: raster changed connectivity: {region.count()} != {expected}")
        dev["connected_components"] = expected
        top.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans()))
        top.insert(kdb.CellInstArray(ly.cell(aliases[f"{dev['label']}_label"]).cell_index(), kdb.Trans()))
    region = kdb.Region(top.begin_shapes_rec(layer)).merged()
    if region.area() != source_area:
        raise RuntimeError("Devices or labels overlap")
    box = region.bbox()
    if min(box.left, box.bottom) < 0 or max(box.right, box.top) > FIELD_NM:
        raise RuntimeError("Layout extends outside the 500 um field")
    ly.write(str(gds_path))
    # Read the final assembled stream independently and compare the full exposed region.
    readback = kdb.Layout()
    readback.read(str(gds_path))
    actual = kdb.Region(readback.cell(top.name).begin_shapes_rec(readback.layer(1, 0))).merged()
    if not (actual ^ region).is_empty():
        raise RuntimeError("Assembled GDS readback differs from PAT geometry")
    render(gds_path, top.name, output / f"{stem}_preview.png")
    rows = []
    for dev in devices:
        r, g = dev["record"], dev["geometry"]
        row = {"label": dev["label"], "geometry_id": r["geometry_id"], "nx": g["nx"], "ny": g["ny"],
               "ax_nm": g["ax_nm"], "ay_nm": g["ay_nm"],
               "major_semiaxis_nm": 1000*r["major_semiaxis_um"],
               "minor_semiaxis_nm": 1000*r["minor_semiaxis_um"], "phi_deg": r["rotation_deg_ccw"],
               "source_gap_x_nm": 1000*r["signed_axial_gap_x_um"],
               "source_gap_y_nm": 1000*r["signed_axial_gap_y_um"],
               "written_gap_x_nm": g["written_centerline_gaps_nm"][0],
               "written_gap_y_nm": g["written_centerline_gaps_nm"][1],
               "components": dev["connected_components"],
               **dict(zip(("xmin_nm", "ymin_nm", "xmax_nm", "ymax_nm"), dev["bbox_nm"]))}
        rows.append(row)
    with (output / f"{stem}_devices.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    result = {"set": letter, "top_cell": top.name, "devices": rows, "dbu_nm": 1,
              "layer_datatype": [1, 0], "n_structures": len(names), "roles_per_device": 9,
              "summed_pat_area_nm2": source_area, "merged_gds_area_nm2": actual.area(),
              "pat_gds_xor_area_nm2": 0, "connectivity_matches_source": True,
              "v30_status": "pending native ECP export", "qualified_for_exposure": False,
              "component_conversion": conversion}
    (output / f"{stem}_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Set {letter}: 8 devices, {len(names)} structures, exact GDS/PAT match; native V30 pending", flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", type=Path, help="lattice_sets_results.txt")
    ap.add_argument("--output", type=Path, default=HERE)
    args = ap.parse_args()
    records = parse_report(args.report)
    # A failed rebuild must not leave an old success manifest beside new data.
    # Regenerate to a fresh directory, then compare or replace deliberately.
    if any(args.output.glob("set_*.*")) or (args.output / "manifest.json").exists():
        ap.error("Output already contains a layout; choose a fresh --output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    source = {"source_path": str(args.report.resolve()), "source_sha256": sha256(args.report),
              "records": records}
    (args.output / "geometry_catalog.json").write_text(json.dumps(source, indent=2), encoding="utf-8")
    for letter in "ABC":
        build_set(letter, records, args.output)
    files = sorted(args.output.glob("set_*.*"))
    manifest = {"source_sha256": source["source_sha256"], "sets": list("ABC"),
                "software_versions": {"numpy": np.__version__, "gdstk": gdstk.__version__, "klayout": kdb.__version__},
                "current_pA": CURRENT_PA, "increment_nm": INCREMENT, "dwell_ns": DWELL_NS,
                "geometry_max_raster_nm": MAX_PIXEL_NM, "device_bbox_limit_nm": SIZE_NM,
                "field_size_nm": FIELD_NM, "field_copies_per_set": 1,
                "finite_boundary": "Nx by Ny whole mesas; exterior rounded caps; midplane component partitions",
                "geometry_validation_passed": True, "v30_status": "pending native ECP export",
                "files": {p.name: sha256(p) for p in files}, "qualified_for_exposure": False}
    manifest["files"]["geometry_catalog.json"] = sha256(args.output / "geometry_catalog.json")
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
