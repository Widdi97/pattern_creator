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
from calibration import circle_union_rects

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
# A compact 3-by-3 ring reserves the central tile for calibration. Tile
# centres include the label footprint, so the complete group is centred.
TILE_CENTRES_NM = ((150_000, 360_000), (250_000, 360_000), (350_000, 360_000),
                   (150_000, 250_000), (350_000, 250_000),
                   (150_000, 140_000), (250_000, 140_000), (350_000, 140_000))
REFERENCE_DIAMETER_NM = 36_000  # User-requested reference, one per field.
DIAMETERS_NM = (600, 1000, 1500, 2000, 3000, 4000, 6000)  # User-specified sweep.
DIMER_DIAMETER_NM = 1800
DIMER_RATIOS = tuple(value / 10 for value in range(8, 14))  # User: v = 0.8 to 1.3.


def calibration_structures(letter):
    """Put numbered references in the unoccupied central 90 x 103 um tile."""
    specs = [(9, "reference", REFERENCE_DIAMETER_NM, 0, (250_000, 278_000), None)]
    for index, diameter in enumerate(DIAMETERS_NM):
        specs.append((10 + index, "diameter", diameter, 0, (214_000 + 12_000 * index, 245_000), None))
    for index, ratio in enumerate(DIMER_RATIOS):
        centre = (212_500 + 15_000 * index, 222_000)
        specs.append((10 + len(DIAMETERS_NM) + index, "dimer", DIMER_DIAMETER_NM,
                      round(ratio * DIMER_DIAMETER_NM), centre, ratio))
    parts, rows = [], []
    for number, kind, diameter, separation, (cx, cy), ratio in specs:
        name = f"{letter}_cal_{number}"
        rects = circle_union_rects(diameter, separation, MAX_PIXEL_NM)
        rects += np.array([cx, cy, cx, cy])
        # Small numerical IDs refer to the calibration CSV. They fit below
        # each reference without consuming the lattice-to-lattice clearances.
        label_y = 254_000 if kind == "reference" else cy - 7000
        label = T.label_rects(str(number), cx - 2500, label_y, height=3000)
        parts.extend(((name, rects), (f"{name}_label", label)))
        rows.append({"label": number, "kind": kind, "diameter_nm": diameter,
                     "centre_distance_nm": separation if kind == "dimer" else "",
                     "a_over_d": ratio if ratio is not None else "",
                     "signed_gap_nm": separation - diameter if kind == "dimer" else "",
                     "centre_x_nm": cx, "centre_y_nm": cy,
                     "structure": name})
    return parts, rows


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def render(path, top_name, output, box=None):
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
                                 box if box is not None else kdb.DBox(0, 0, 500, 500), False)
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
        cx, cy = TILE_CENTRES_NM[index]
        dx = cx - round((int(bbox[0]) + int(bbox[2])) / 2)
        dy = cy + 6500 - round((int(bbox[1]) + int(bbox[3])) / 2)
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
        lab = T.label_rects(str(index + 1), int(bbox[0] + dx),
                            int(bbox[1] + dy - 13_000), height=8_000)
        pat_lines.append(T.structure(label_name, lab, increment=INCREMENT, dwell=DWELL_NS))
        names.append(label_name)
        source_area += area + int(np.sum((lab[:, 2] - lab[:, 0]) * (lab[:, 3] - lab[:, 1])))
        devices.append({"label": label, "record": record, "geometry": dev,
                        "parts": shifted, "area_nm2": area, "offset_nm": (int(dx), int(dy)),
                        "bbox_nm": (bbox + np.array([dx, dy, dx, dy])).tolist()})
    calibration_parts, calibration_rows = calibration_structures(letter)
    for name, rects in calibration_parts:
        pat_lines.append(T.structure(name, rects, increment=INCREMENT, dwell=DWELL_NS))
        names.append(name)
        source_area += int(np.sum((rects[:, 2] - rects[:, 0]) * (rects[:, 3] - rects[:, 1])))
    pat_path = output / f"{stem}.pat"
    pat_path.write_text("".join(pat_lines), encoding="ascii")
    ctl = (f"; Anisotropic KPZ Set {letter}; one field, one copy\n"
           f"current = {CURRENT_PA}\norigin = 0, 0\nx = 0\ny = 0\nstage\n"
           f"sfile = {stem}\n" + "".join(f"draw({name})\n" for name in names) + "END\n")
    (output / f"{stem}.ctl").write_text(ctl, encoding="ascii")
    definitions = parse_pat(pat_path.read_text())
    if {d.name for d in definitions} != set(names) or len(names) != len(set(names)):
        raise RuntimeError("CTL must draw every PAT definition exactly once")
    if sum(line.strip() == "stage" for line in ctl.splitlines()) != 1:
        raise RuntimeError("A set must use exactly one stage position")
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
    calibration_cell = ly.create_cell(f"{letter}_CALIBRATION")
    for name, rects in calibration_parts:
        calibration_cell.insert(kdb.CellInstArray(ly.cell(aliases[name]).cell_index(), kdb.Trans()))
    top.insert(kdb.CellInstArray(calibration_cell.cell_index(), kdb.Trans()))
    region = kdb.Region(top.begin_shapes_rec(layer)).merged()
    if region.area() != source_area:
        raise RuntimeError("Devices or labels overlap")
    box = region.bbox()
    if min(box.left, box.bottom) < 0 or max(box.right, box.top) > FIELD_NM:
        raise RuntimeError("Layout extends outside the 500 um field")
    # This central envelope includes calibration, labels and all lattice caps.
    if min(box.left, box.bottom) < 85_000 or max(box.right, box.top) > 415_000:
        raise RuntimeError("Layout no longer fits the compact central envelope")
    ly.write(str(gds_path))
    # Read the final assembled stream independently and compare the full exposed region.
    readback = kdb.Layout()
    readback.read(str(gds_path))
    actual = kdb.Region(readback.cell(top.name).begin_shapes_rec(readback.layer(1, 0))).merged()
    if not (actual ^ region).is_empty():
        raise RuntimeError("Assembled GDS readback differs from PAT geometry")
    render(gds_path, top.name, output / f"{stem}_preview.png")
    render(gds_path, top.name, output / f"{stem}_calibration_preview.png",
           kdb.DBox(200, 195, 300, 305))
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
               **dict(zip(("xmin_nm", "ymin_nm", "xmax_nm", "ymax_nm"), dev["bbox_nm"])),
               "width_um": (dev["bbox_nm"][2] - dev["bbox_nm"][0]) / 1000,
               "height_um": (dev["bbox_nm"][3] - dev["bbox_nm"][1]) / 1000}
        rows.append(row)
    with (output / f"{stem}_devices.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    with (output / f"{stem}_calibrations.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=calibration_rows[0])
        writer.writeheader()
        writer.writerows(calibration_rows)
    result = {"set": letter, "top_cell": top.name, "devices": rows, "dbu_nm": 1,
              "layer_datatype": [1, 0], "n_structures": len(names), "roles_per_device": 9,
              "calibrations": calibration_rows, "stage_positions": 1,
              "field_content_bbox_nm": [box.left, box.bottom, box.right, box.top],
              "max_bbox_radius_from_field_centre_um": float(max(
                  np.hypot(x - FIELD_NM / 2, y - FIELD_NM / 2)
                  for x in (box.left, box.right) for y in (box.bottom, box.top)) / 1000),
              "summed_pat_area_nm2": source_area, "merged_gds_area_nm2": actual.area(),
              "pat_gds_xor_area_nm2": 0, "connectivity_matches_source": True,
              "v30_status": "pending native ECP export", "qualified_for_exposure": False,
              "component_conversion": conversion}
    (output / f"{stem}_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Set {letter}: 8 lattices, {len(calibration_rows)} calibrations, one stage position, exact GDS/PAT match", flush=True)
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
                "placement": "centred 3x3 ring, references in central tile",
                "reference_diameter_nm": REFERENCE_DIAMETER_NM,
                "diameter_series_nm": list(DIAMETERS_NM), "dimer_diameter_nm": DIMER_DIAMETER_NM,
                "dimer_a_over_d": list(DIMER_RATIOS),
                "finite_boundary": "Nx by Ny whole mesas; exterior rounded caps; midplane component partitions",
                "geometry_validation_passed": True, "v30_status": "pending native ECP export",
                "files": {p.name: sha256(p) for p in files}, "qualified_for_exposure": False}
    manifest["files"]["geometry_catalog.json"] = sha256(args.output / "geometry_catalog.json")
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
