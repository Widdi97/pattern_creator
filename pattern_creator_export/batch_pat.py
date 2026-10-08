"""Inventory/export archived PAT libraries without importing project scripts."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from .pat import INPUT_SCALE_ASSUMPTION, export_pat, parse_pat


PAT_LINE = re.compile(r"^\s*(D |RECT |CIRCLE |XPOLY |YPOLY )", re.MULTILINE | re.IGNORECASE)


def decode_source(raw):
    try:
        return raw.decode("utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        return raw.decode("cp1252"), "cp1252"


def run(source, output, *, export=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source or source in output.parents:
        raise ValueError("output must be outside the original source repository")
    if export and ((output / "export_ledger.json").exists() or next(output.rglob("*.gds"), None) is not None):
        raise ValueError("export output already contains GDS files or an export ledger; use a fresh output directory")
    files, projects = [], {}
    for root_name in ("projects", "examples"):
        root = source / root_name
        for directory in sorted(root.iterdir()):
            if directory.is_dir() and directory.name != "__pycache__":
                key = directory.relative_to(source).as_posix()
                projects[key] = {"python_source_files": len(list(directory.rglob("*.py"))),
                                 "stored_pat_candidates": 0, "exported": 0, "rejected": 0}
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in (".pat", ".txt"):
                continue
            relative = path.relative_to(source)
            project = "/".join(relative.parts[:2])
            record = {"source": relative.as_posix()}
            projects.setdefault(project, {"python_source_files": 0, "stored_pat_candidates": 0,
                                          "exported": 0, "rejected": 0})
            try:
                raw = path.read_bytes()
                record.update(source_sha256=hashlib.sha256(raw).hexdigest(), source_bytes=len(raw))
                content, encoding = decode_source(raw)
                if path.suffix.lower() != ".pat" and not PAT_LINE.search(content):
                    continue
                counts = Counter(line.strip().split()[0].upper() for line in content.splitlines()
                                 if line.strip() and not line.strip().startswith(";"))
                record.update(encoding=encoding, statement_counts=dict(counts))
                definitions = parse_pat(content)
                record.update(status="parsed", definitions=len(definitions),
                              array_definitions=sum(d.repetition is not None for d in definitions),
                              geometry_count=sum(len(d.geometry) for d in definitions))
                if export:
                    # Retain the original extension in the basename: foo.pat
                    # and foo.txt can coexist without output collisions.
                    destination = output / relative.with_name(relative.name + ".gds")
                    report = export_pat(definitions, destination)
                    record.update(report, status="exported", output=destination.relative_to(output).as_posix())
                    projects[project]["exported"] += 1
                print(f"{record['status']}: {relative.as_posix()}", flush=True)
            except Exception as error:
                record.update(status="rejected", error=f"{type(error).__name__}: {error}")
                projects[project]["rejected"] += 1
                print(f"rejected: {relative.as_posix()}: {error}", flush=True)
            projects[project]["stored_pat_candidates"] += 1
            files.append(record)
    summary = Counter(record["status"] for record in files)
    for record in projects.values():
        record["coverage"] = ("no_stored_PAT_geometry" if not record["stored_pat_candidates"]
                              else "all_stored_candidates_exported" if record["exported"] == record["stored_pat_candidates"]
                              else "partial_stored_export" if record["exported"]
                              else "inventory_only" if not export else "all_stored_candidates_rejected")
    result = {"source_repository": str(source), "mode": "export" if export else "dry_run",
              "scope": "archived PAT definition libraries, source-defined components only; project scripts and CTL not executed",
              "input_scale_assumption": INPUT_SCALE_ASSUMPTION,
              "units_basis": "project convention: generate_pattern.Text.fontsize comment and ring_resonators_ecp diameter names/conversions; PAT default pixel calibration is not inferred",
              "numeric_primitive_basis": {"manual": "https://www.ipsiras.ru/Lab/CKPO/Nanofot/doc/XENOSXeDraw2.pdf",
                                          "edition": "8 September 2010", "section": "Appendix B.1, page 111: P0 = RECT",
                                          "repository_confirmation": "projects/ring_resonators_ecp/numbers.py:11-35"},
              "supported": ["D name[, dx, dy, nx, ny]", "I", "C", "RECT", "P 0, x0, y0, x1, y1", "CIRCLE", "XPOLY", "YPOLY", "END", "; full-line comments"],
              "limitations": ["No stage/CTL wafer assembly or exposure semantics exported.",
                              "No inference of absent lattice borders/corners from archived geometry.",
                              "Existing separate D definitions and arrays are preserved; unrelated definitions are not assembled.",
                              "Unknown statements, duplicate names, missing END, degenerate geometry reject the whole file.",
                              "Curves use a 1 nm chord tolerance plus 1 nm database-grid rounding.",
                              "Projects without stored PAT require the separate direct-geometry API or migration."],
              "summary": dict(summary), "candidate_files": len(files),
              "source_bytes": sum(record.get("source_bytes", 0) for record in files),
              "output_bytes": sum(record.get("output_bytes", 0) for record in files),
              "projects": projects, "files": files}
    output.mkdir(parents=True, exist_ok=True)
    ledger = output / ("export_ledger.json" if export else "inventory.json")
    ledger.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"summary": result["summary"], "candidate_files": len(files),
                      "output_bytes": result["output_bytes"], "ledger": str(ledger)}, indent=2), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--export", action="store_true", help="write GDS only after strict parsing and KLayout verification")
    args = parser.parse_args()
    run(args.source, args.output, export=args.export)


if __name__ == "__main__":
    main()
