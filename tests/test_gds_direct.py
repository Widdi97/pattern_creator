"""Independent KLayout read-back oracles for the direct-geometry prototype."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import klayout.db as kdb
import numpy as np

from pattern_creator_export.direct import DirectLattice, DirectPattern, ShapeSpec


def read(path):
    layout = kdb.Layout()
    layout.read(str(path))
    return layout


def region(layout, cell_name, layer=1, datatype=0):
    cell = layout.cell(cell_name)
    return kdb.Region(cell.begin_shapes_rec(layout.layer(layer, datatype))).merged()


def boxes(xs, ys):
    result = kdb.Region()
    for x0, x1 in xs:
        for y0, y1 in ys:
            result.insert(kdb.Box(x0, y0, x1, y1))
    return result.merged()


class DirectExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "layout.gds"

    def assertRegionEqual(self, actual, expected):
        self.assertTrue((actual ^ expected).is_empty(), str((actual ^ expected).bbox()))

    def test_ordered_subtraction_hole_and_readded_island(self):
        pattern = DirectPattern(2000, 2000, 100)
        for points, operation in [
            ((-200, -200, 2200, -200, 2200, 2200, -200, 2200), "add"),
            ((500, 500, 1500, 500, 1500, 1500, 500, 1500), "subtract"),
            ((700, 700, 1300, 700, 1300, 1300, 700, 1300), "add"),
        ]:
            pattern.add_parametrized_shape("polygon", *points, boolean_operation=operation)
        metadata = pattern.export_gds(self.path, layer=23, datatype=7)
        layout = read(self.path)
        self.assertEqual(layout.dbu, 0.001)  # KLayout coordinates below are integer nm.
        expected = (kdb.Region(kdb.Box(-50, -50, 1950, 1950))
                    - kdb.Region(kdb.Box(500, 500, 1500, 1500))
                    + kdb.Region(kdb.Box(700, 700, 1300, 1300)))
        actual = region(layout, "PATTERN", 23, 7)
        self.assertRegionEqual(actual, expected)
        self.assertEqual(actual.area(), 3360000)
        self.assertEqual(metadata["support_nm"], [[-50, -50], [1950, 1950]])

    def test_curves_have_pitch_independent_polygonization(self):
        results = []
        for pitch in (10, 500):
            p = DirectPattern(10000, 10000, pitch)
            p.add_parametrized_shape("circle", 2500, 2500, 1000, boolean_operation="add")
            p.add_parametrized_shape("ellipse", 7000, 7000, 800, 300, np.pi / 2,
                                    boolean_operation="add")
            p.export_gds(self.path)
            results.append(region(read(self.path), "PATTERN"))
        self.assertRegionEqual(*results)
        self.assertAlmostEqual(results[0].area(), np.pi * (1000**2 + 800 * 300), delta=11000)

    def test_sampled_custom_curve_and_no_implicit_sampling(self):
        def curve(t, x, y, radius):
            return x + radius * np.cos(2 * np.pi * t), y + radius * np.sin(2 * np.pi * t)

        p = DirectPattern(2000, 2000, 10)
        with self.assertRaisesRegex(ValueError, "samples"):
            p.add_parametrized_shape(curve, 1000, 1000, 500, boolean_operation="add")
        p.add_parametrized_shape(curve, 1000, 1000, 500, boolean_operation="add", samples=257)
        p.export_gds(self.path)
        self.assertAlmostEqual(region(read(self.path), "PATTERN").area(), np.pi * 500**2, delta=1500)
        with self.assertRaises(TypeError):
            p.add_parametrized_shape("circle", 1, 2, 3)
        with self.assertRaises(ValueError):
            p.add_parametrized_shape("circle", 1, 2, 3, boolean_operation="xor")

    def test_all_nine_legacy_cells_and_aligned_array_placement(self):
        shape = ShapeSpec("polygon", (-50, -50, 50, -50, 50, 50, -50, 50), "add")
        lattice = DirectLattice((1000, 0), (0, 1000), 3000, 2000, 100,
                                [shape], [(0, 0)], pattern_name="TEST")
        metadata = lattice.export_gds(self.path)
        layout = read(self.path)
        low, high, both = [(-50, 0)], [(900, 950)], [(-50, 0), (900, 950)]
        # Hand-derived from legacy generate_unit_cells shifts and generate_patterns
        # offsets, with the four extra +Ay corner shifts removed in this GDS assembly.
        expected = {
            "BULK": (both, both, (2000, 2000), 3, 2),
            "LEFT": (high, both, (1000, 2000), 1, 2),
            "RIGHT": (low, both, (5000, 2000), 1, 2),
            "BOTTOM": (both, high, (2000, 1000), 3, 1),
            "TOP": (both, low, (2000, 4000), 3, 1),
            "CORNER_BL": (high, high, (1000, 1000), 1, 1),
            "CORNER_TL": (high, low, (1000, 4000), 1, 1),
            "CORNER_BR": (low, high, (5000, 1000), 1, 1),
            "CORNER_TR": (low, low, (5000, 4000), 1, 1),
        }
        top_expected = kdb.Region()
        for role, (xs, ys, origin, columns, rows) in expected.items():
            local = boxes(xs, ys)
            self.assertRegionEqual(region(layout, "TEST_" + role), local)
            entry = next(cell for cell in metadata["cells"] if cell["role"] == role)
            self.assertEqual(entry["origin_nm"], list(origin))
            self.assertEqual((entry["columns"], entry["rows"]), (columns, rows))
            for i in range(columns):
                for j in range(rows):
                    top_expected += local.transformed(kdb.Trans(origin[0] + 1000 * i,
                                                                origin[1] + 1000 * j))
        self.assertRegionEqual(region(layout, "TEST"), top_expected)
        # The independent finite-site oracle requires twelve complete, separated
        # squares: top/bottom corner quarters close exactly against border ends.
        finite_sites = boxes([(1900 + 1000*i, 2000 + 1000*i) for i in range(4)],
                             [(1900 + 1000*j, 2000 + 1000*j) for j in range(3)])
        self.assertRegionEqual(region(layout, "TEST"), finite_sites)
        self.assertEqual(region(layout, "TEST").count(), 12)
        self.assertEqual(len(list(layout.cell("TEST").each_inst())), 9)
        self.assertEqual(layout.cells(), 10)
        self.assertEqual(metadata["placement"], "aligned_grid_components")
        self.assertFalse(metadata["process_qualified"])

    def test_empty_borders_and_corners_are_still_exported(self):
        lattice = DirectLattice((1000, 0), (0, 1000), 3000, 2000, 100,
                                [], np.empty((0, 2)))
        metadata = lattice.export_gds(self.path)
        layout = read(self.path)
        self.assertEqual(layout.cells(), 10)
        self.assertEqual(len(list(layout.cell("LATTICE").each_inst())), 9)
        for entry in metadata["cells"]:
            self.assertIsNotNone(layout.cell(entry["cell"]))
            self.assertTrue(region(layout, entry["cell"]).is_empty())

    def test_fractional_period_uses_legacy_floor_division_and_rounded_pitch(self):
        lattice = DirectLattice((1000.1, 0), (0, 1000.2), 5000.5, 5001, 100,
                                [], np.empty((0, 2)))
        metadata = lattice.export_gds(self.path)
        self.assertEqual(metadata["counts"], [4, 4])  # // differs here from floor(size / period).
        self.assertEqual(metadata["array_pitch_nm"], [1000, 1000])
        layout = read(self.path)
        bulk = next(i for i in layout.cell("LATTICE").each_inst() if i.cell.name.endswith("_BULK"))
        self.assertEqual((bulk.na, bulk.nb), (4, 4))
        self.assertEqual({(bulk.a.x, bulk.a.y), (bulk.b.x, bulk.b.y)}, {(1000, 0), (0, 1000)})
        right = next(i for i in layout.cell("LATTICE").each_inst() if i.cell.name.endswith("_RIGHT"))
        self.assertEqual((right.trans.disp.x, right.trans.disp.y), (6000, 2000))

    def test_fractional_components_share_abutting_integer_support(self):
        shape = ShapeSpec("polygon", (-50, -50, 50, -50, 50, 50, -50, 50), "add")
        lattice = DirectLattice((1000.6, 0), (0, 1000.8), 5000, 5000, 100,
                                [shape], [(0, 0)])
        metadata = lattice.export_gds(self.path)
        self.assertEqual(metadata["array_pitch_nm"], [1001, 1001])
        self.assertEqual(metadata["support_nm"], [[-45, -45], [956, 956]])
        layout = read(self.path)
        origins = {entry["role"]: np.asarray(entry["origin_nm"]) for entry in metadata["cells"]}
        self.assertEqual(origins["BULK"].tolist(), [2001, 2002])
        expected_origins = {
            "LEFT": [1000, 2002], "RIGHT": [6005, 2002],
            "BOTTOM": [2001, 1001], "TOP": [2001, 6006],
            "CORNER_BL": [1000, 1001], "CORNER_TL": [1000, 6006],
            "CORNER_BR": [6005, 1001], "CORNER_TR": [6005, 6006],
        }
        for role, origin in expected_origins.items():
            self.assertEqual(origins[role].tolist(), origin)
        # Every repeated support and terminal component meet on the same integer
        # boundary: left/right borders and all four corner endpoints abut exactly.
        self.assertEqual(origins["LEFT"][0] + 956, origins["BULK"][0] - 45)
        self.assertEqual(origins["BULK"][0] + 3*1001 + 956, origins["RIGHT"][0] - 45)
        self.assertEqual(origins["BOTTOM"][1] + 956, origins["BULK"][1] - 45)
        self.assertEqual(origins["BULK"][1] + 3*1001 + 956, origins["TOP"][1] - 45)
        for role, corner in [("LEFT", "CORNER_TL"), ("RIGHT", "CORNER_TR")]:
            self.assertEqual(origins[role][1] + 3*1001 + 956, origins[corner][1] - 45)
        for entry in metadata["cells"]:
            bounds = region(layout, entry["cell"]).bbox()
            self.assertGreaterEqual(bounds.left, -45)
            self.assertGreaterEqual(bounds.bottom, -45)
            self.assertLessEqual(bounds.right, 956)
            self.assertLessEqual(bounds.top, 956)

    def test_repeatable_bytes_and_coordinate_range_guards(self):
        pattern = DirectPattern(2000, 2000, 100)
        pattern.add_parametrized_shape("circle", 1000, 1000, 100, boolean_operation="add")
        pattern.export_gds(self.path)
        first = self.path.read_bytes()
        pattern.export_gds(self.path)
        self.assertEqual(first, self.path.read_bytes())
        large = DirectPattern(3e9, 1000, 1000)
        with self.assertRaisesRegex(ValueError, "32-bit"):
            large.add_parametrized_shape("polygon", 2.5e9, 0, 2.6e9, 0, 2.6e9, 100, 2.5e9, 100,
                                        boolean_operation="add")
        # Even empty cells must have representable reference origins/endpoints.
        lattice = DirectLattice((1e9, 0), (0, 1e9), 2e9, 1e9, 1e8,
                                [], np.empty((0, 2)))
        with self.assertRaisesRegex(ValueError, "32-bit"):
            lattice.export_gds(self.path)
        self.assertEqual(first, self.path.read_bytes())

    def test_curve_preflight_rejects_before_native_polygon_allocation(self):
        with patch("pattern_creator_export.direct.gdstk.ellipse") as native:
            pattern = DirectPattern(2000, 2000, 100)
            with self.assertRaisesRegex(ValueError, "32-bit"):
                pattern.add_parametrized_shape("circle", 0, 0, 1e20, boolean_operation="add")
            with self.assertRaisesRegex(ValueError, "32-bit"):
                pattern.add_parametrized_shape("ellipse", 0, 0, 1e20, 1e19, .2,
                                                boolean_operation="add")
            fine = DirectPattern(2000, 2000, 100, tolerance_nm=1e-20)
            with self.assertRaisesRegex(ValueError, "1000000 vertices"):
                fine.add_parametrized_shape("circle", 1000, 1000, 500, boolean_operation="add")
            native.assert_not_called()

    def test_unsupported_lattice_is_explicit(self):
        for a1, a2, size in [((0, 1000), (1000, 0), 3000),
                             ((1000, 0), (np.sqrt(2) * 1000, 1000), 3000),
                             ((1000, 0), (0, 1000), 500)]:
            with self.assertRaises(ValueError):
                DirectLattice(a1, a2, size, size, 100, [], np.empty((0, 2)))
        with self.assertRaises(ValueError):
            DirectPattern(1000, 1000, 100, pattern_name="bad name")
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            DirectLattice((1000, 0), (0, 1000), 2000, 2000, 100,
                          [ShapeSpec("circle", (0, 0, 20), "add", lattice_margin_nm=-1)], [(0, 0)])


if __name__ == "__main__":
    unittest.main()
