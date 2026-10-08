"""Exercise the real raycast API and its optional GDS bridge."""

from collections import Counter
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("MPLBACKEND", "Agg")

import klayout.db as kdb
import numpy as np

import generate_pattern
import pattern_creator_export
from generate_pattern import Lattice, Pattern, circle, polygon
from pattern_creator_export.pat import export_pat, parse_pat


def read_region(path):
    layout = kdb.Layout()
    layout.read(str(path))
    return kdb.Region(layout.top_cell().begin_shapes_rec(layout.layer(1, 0))).merged()


class LegacyGdsTests(unittest.TestCase):
    def test_raycast_subtraction_preserves_pat_and_hole(self):
        pattern = Pattern(800, 800, 100, pattern_name="RAYCAST", increment=2, dwell_time=200)
        pattern.add_parametrized_shape(polygon, 0, 0, 600, 0, 600, 600, 0, 600)
        pattern.add_parametrized_shape(polygon, 200, 200, 400, 200, 400, 400, 200, 400,
                                       boolean_operation="subtract")
        text = pattern.export_pattern(complete=True)
        # Frozen from the unmodified legacy implementation before integration.
        self.assertEqual(text, "D RAYCAST\nI 2\nC 200\n"
                         "RECT -50, -50, 150, 550\nRECT 150, -50, 350, 150\n"
                         "RECT 150, 350, 350, 550\nRECT 350, -50, 550, 550\nEND")
        mask, rectangles = pattern.pattern.copy(), np.asarray(pattern.rects).copy()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "raycast.gds"
            export_pat(parse_pat(text), output)
            expected = kdb.Region(kdb.Box(-50, -50, 550, 550)) - kdb.Region(kdb.Box(150, 150, 350, 350))
            self.assertTrue((read_region(output) ^ expected).is_empty())
        np.testing.assert_array_equal(pattern.pattern, mask)
        np.testing.assert_array_equal(pattern.rects, rectangles)
        self.assertEqual(pattern.export_pattern(complete=True), text)

    def test_anisotropic_raycast_with_export_offset(self):
        pattern = Pattern(800, 900, np.array([100, 150]))
        pattern.add_parametrized_shape(polygon, 0, 0, 600, 0, 600, 600, 0, 600)
        text = pattern.export_pattern(complete=True, offsetx=1000, offsety=-200)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "offset.gds"
            export_pat(parse_pat(text), output)
            expected = kdb.Region(kdb.Box(950, -275, 1550, 325))
            self.assertTrue((read_region(output) ^ expected).is_empty())

    def test_legacy_lattice_keeps_all_nine_definitions(self):
        # Suppress only the constructor's diagnostic plot, not geometry generation.
        with patch.object(Lattice, "plot_lattice_vecs"):
            lattice = Lattice(np.array([1000, 0]), np.array([0, 1000]), 3000, 2000, 100,
                              [[circle, 0, 0, 200]], np.array([[0, 0]]), pattern_name="LEGACY")
        text = lattice.pat_str
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "legacy_lattice.gds"
            report = export_pat(parse_pat(text), output)
            self.assertEqual(Counter(cell["role_from_name"] for cell in report["cells"]),
                             {"bulk": 1, "border": 4, "corner": 4})
            layout = kdb.Layout()
            layout.read(str(output))
            self.assertEqual({cell["source_name"] for cell in report["cells"]},
                             {f"LEGACY_x_{x}_y_{y}" for x in (-1, 0, 1) for y in (-1, 0, 1)})
            # Negative index names contain '-' and receive portable GDS aliases;
            # the report must retain a unique mapping back to all source names.
            self.assertEqual({cell.name for cell in layout.top_cells()},
                             {cell["gds_cell"] for cell in report["cells"]})
            self.assertEqual(len(layout.top_cells()), 9)
        self.assertEqual(lattice.pat_str, text)

    def test_legacy_and_package_root_work_without_gds_dependencies(self):
        # Use a fresh interpreter so already-loaded test dependencies cannot hide
        # an accidental mandatory GDS import in the old API or new package root.
        code = """
import sys
sys.path[:0] = sys.argv[1:]
class BlockGds:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'gdstk', 'klayout'}:
            raise ImportError('optional GDS dependency blocked by compatibility test')
sys.meta_path.insert(0, BlockGds())
import pattern_creator_export
from generate_pattern import Pattern, polygon
p = Pattern(400, 400, 100)
p.add_parametrized_shape(polygon, 0, 0, 300, 0, 300, 300, 0, 300)
assert 'RECT -50, -50, 250, 250' in p.export_pattern(complete=True)
assert not any(name.split('.')[0] in {'gdstk', 'klayout'} for name in sys.modules)
"""
        package_root = Path(pattern_creator_export.__file__).resolve().parent.parent
        legacy_root = Path(generate_pattern.__file__).resolve().parent
        result = subprocess.run([sys.executable, "-B", "-c", code, str(package_root), str(legacy_root)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
