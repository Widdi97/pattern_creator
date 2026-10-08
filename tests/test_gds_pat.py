import tempfile
from collections import Counter
from contextlib import redirect_stdout
import io
from pathlib import Path
import unittest
from unittest.mock import patch

import klayout.db as kdb

from pattern_creator_export.pat import PatError, export_pat, parse_pat, polygon_points, validate_gds
from pattern_creator_export.batch_pat import run


class PatTests(unittest.TestCase):
    def definition(self, body, header="D sample"):
        return header + "\nI 16\nC 122\n" + body + "\nEND\n"

    def test_rectangle_circle_and_ring_trapezoids(self):
        source = self.definition("RECT -100, -200, 300, 400\nCircle 1000, 1000, 500\n"
                                 "XPOLY 0, 0, 100, 200, 50, 100\nYPOLY 0, 0, 100, 200, 100, 50")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"library.gds"
            report = export_pat(parse_pat(source), path)
            self.assertTrue(report["validation"]["passed"])
            layout = kdb.Layout()
            layout.read(str(path))
            cell = layout.cell("sample")
            self.assertEqual(cell.bbox(), kdb.Box(-100, -200, 1500, 1500))
            self.assertEqual(report["cells"][0]["geometry_counts"],
                             {"RECT": 1, "CIRCLE": 1, "XPOLY": 1, "YPOLY": 1})

    def test_verified_trapezoid_mapping(self):
        self.assertEqual(polygon_points("XPOLY", (1, 2, 3, 4, 5, 6)),
                         [(1, 2), (3, 2), (4, 6), (5, 6)])
        self.assertEqual(polygon_points("YPOLY", (1, 2, 3, 4, 5, 6)),
                         [(1, 2), (1, 3), (5, 4), (5, 6)])

    def test_bulk_border_corner_and_repetitions_stay_separate(self):
        source = (self.definition("RECT 0, 0, 100, 200", "D lattice_x_0_y_0, 1000, 2000, 3, 4")
                  + self.definition("RECT 0, 0, 100, 200", "D lattice_x_1_y_0, 1000, 2000, 1, 4")
                  + self.definition("RECT 0, 0, 100, 200", "D lattice_x_1_y_1"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"lattice.gds"
            report = export_pat(parse_pat(source), path)
            layout = kdb.Layout()
            layout.read(str(path))
            self.assertEqual(len(layout.top_cells()), 3)
            self.assertEqual(layout.cell("lattice_x_0_y_0").bbox(), kdb.Box(0, 0, 2100, 6200))
            self.assertEqual([cell["role_from_name"] for cell in report["cells"]], ["bulk", "border", "corner"])
            self.assertEqual(report["validation"]["references_checked"], 2)

    def test_single_member_array_and_long_name(self):
        source = self.definition("RECT 0, 0, 100, 100", "D " + "name"*15 + ", 1000, 1000, 1, 1")
        with tempfile.TemporaryDirectory() as directory:
            report = export_pat(parse_pat(source), Path(directory)/"single.gds")
            self.assertLessEqual(len(report["cells"][0]["gds_cell"]), 32)
            self.assertEqual(report["cells"][0]["source_name"], "name"*15)

    def test_reject_unknown_or_incomplete_without_partial_output(self):
        cases = [self.definition("P 1, 1, 2, 3, 4"), "D no_end\nI 16\nC 100\n",
                 self.definition("RECT 0, 0, 0, 100"), self.definition("CIRCLE 0, 0, -1"),
                 self.definition("XPOLY 0, 0, 100, 0, 100, 100"),
                 self.definition("RECT 0, 0, 100, 100")*2,
                 self.definition("RECT 0, 0, 100, 100", "D bad, 0, 10, 2, 2")]
        for source in cases:
            with self.subTest(source=source), self.assertRaises(PatError):
                parse_pat(source)

    def test_comments_empty_cells_and_case(self):
        source = "; archived comment\nD empty\nI 16\nC 122\nEnd\n"
        with tempfile.TemporaryDirectory() as directory:
            report = export_pat(parse_pat(source), Path(directory)/"empty.gds")
            self.assertEqual(report["validation"]["polygon_coordinate_signatures_checked"], 0)

    def test_overflow_rejected_before_file_is_created(self):
        source = self.definition("RECT 0, 0, 100, 100", "D huge, 1000000000, 100, 3, 1")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"huge.gds"
            with self.assertRaisesRegex(PatError, "array endpoint"):
                export_pat(parse_pat(source), path)
            self.assertFalse(path.exists())

    def test_independent_reader_detects_changed_coordinates(self):
        source = self.definition("RECT 0, 0, 100, 200")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"changed.gds"
            export_pat(parse_pat(source), path)
            expected = {"sample": {"polygons": Counter({((0, 0), (0, 201), (100, 201), (100, 0)): 1}),
                                   "reference": None}}
            with self.assertRaisesRegex(PatError, "polygon-coordinate mismatch"):
                validate_gds(path, expected)

    def test_huge_source_and_tiny_tolerance_rejected_before_polygon_construction(self):
        cases = [("CIRCLE 0, 0, 1000000000000", 1.0, "source geometry"),
                 ("RECT 0, 0, 1000000000000, 100", 1.0, "source geometry"),
                 ("CIRCLE 0, 0, 100", 1e-300, "1000000 vertices")]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"unsafe.gds"
            for body, tolerance, diagnostic in cases:
                with self.subTest(body=body, tolerance=tolerance), patch("pattern_creator_export.pat._polygons") as construct:
                    with self.assertRaisesRegex(PatError, diagnostic):
                        export_pat(parse_pat(self.definition(body)), path, circle_tolerance_nm=tolerance)
                    construct.assert_not_called()
                    self.assertFalse(path.exists())

    def test_batch_decode_failure_is_recorded_and_other_files_continue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root/"source", root/"output"
            (source/"projects"/"sample").mkdir(parents=True)
            (source/"examples").mkdir()
            (source/"projects"/"sample"/"bad.pat").write_bytes(b"D bad\n\x81")
            (source/"projects"/"sample"/"good.pat").write_text(self.definition("RECT 0, 0, 100, 100"))
            with redirect_stdout(io.StringIO()):
                result = run(source, output)
            self.assertEqual(result["summary"], {"rejected": 1, "parsed": 1})
            self.assertIn("UnicodeDecodeError", result["files"][0]["error"])
            self.assertIn("source_sha256", result["files"][0])
            self.assertEqual(result["projects"]["projects/sample"]["stored_pat_candidates"], 2)

    def test_batch_refuses_previous_export_without_changing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for existing in ("nested/previous.gds", "export_ledger.json"):
                with self.subTest(existing=existing):
                    output = root/str(len(existing))
                    old = output/existing
                    old.parent.mkdir(parents=True)
                    old.write_bytes(b"preserve previous result")
                    with self.assertRaisesRegex(ValueError, "fresh output directory"):
                        run(root/"source", output, export=True)
                    self.assertEqual(old.read_bytes(), b"preserve previous result")

    def test_verified_p0_alias_has_exact_rectangle_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            rectangles = []
            for opcode in ("RECT", "P 0,"):
                path = Path(directory)/("rectangle.gds" if opcode == "RECT" else "p0.gds")
                report = export_pat(parse_pat(self.definition(opcode+" -10, 20, 300, 400")), path)
                self.assertTrue(report["validation"]["passed"])
                self.assertIn("machine field calibration not inferred", report["input_scale_assumption"])
                layout = kdb.Layout()
                layout.read(str(path))
                rectangles.append([(p.x, p.y) for shape in layout.cell("sample").shapes(layout.layer(1, 0)).each()
                                   for p in shape.polygon.each_point_hull()])
            self.assertEqual(rectangles[0], rectangles[1])


if __name__ == "__main__":
    unittest.main()
