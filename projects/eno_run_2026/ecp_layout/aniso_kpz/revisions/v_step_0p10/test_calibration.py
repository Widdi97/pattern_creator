"""Independent centre-occupancy checks for circular calibration geometry."""
import math
import unittest

import numpy as np

from calibration import circle_union_rects


class CircleUnionTests(unittest.TestCase):
    def assert_dense_mask(self, diameter, separation, pixel):
        rects = circle_union_rects(diameter, separation, pixel)
        # Uniform grids here make this independent of the production edge helper.
        radius = diameter / 2
        xs = np.arange(-radius - separation / 2 + pixel / 2,
                       radius + separation / 2, pixel)
        ys = np.arange(-radius + pixel / 2, radius, pixel)
        xx, yy = np.meshgrid(xs, ys)
        expected = ((xx - separation / 2) ** 2 + yy ** 2 <= radius ** 2)
        expected |= ((xx + separation / 2) ** 2 + yy ** 2 <= radius ** 2)
        coverage = np.zeros_like(expected, dtype=np.uint8)
        for x1, y1, x2, y2 in rects:
            coverage[np.searchsorted(ys, y1):np.searchsorted(ys, y2),
                     np.searchsorted(xs, x1):np.searchsorted(xs, x2)] += 1
        np.testing.assert_array_equal(coverage, expected.astype(np.uint8))
        self.assertTrue(np.all(rects[:, 2:] > rects[:, :2]))
        # Every rectangle owns a different x interval; touching edges are fine.
        self.assertTrue(np.all(rects[1:, 0] >= rects[:-1, 2]))

    def test_single_overlap_touch_and_gap_match_dense_union(self):
        for diameter in (40, 100, 1800):
            for ratio in (0, 0.4, 0.8, 1.0, 1.2):
                with self.subTest(diameter=diameter, ratio=ratio):
                    self.assert_dense_mask(diameter, round(diameter * ratio), 2)

    def test_36um_circle_bbox_area_and_symmetry(self):
        rects = circle_union_rects(36_000)
        self.assertEqual(rects.dtype, np.dtype("int64"))
        self.assertEqual(tuple(rects[:, :2].min(0)), (-18_000, -18_000))
        self.assertEqual(tuple(rects[:, 2:].max(0)), (18_000, 18_000))
        area = np.prod(rects[:, 2:] - rects[:, :2], axis=1).sum()
        # Centre occupancy differs from a smooth disk only near its perimeter.
        self.assertLess(abs(area - math.pi * 18_000 ** 2), math.pi * 36_000 * 5)
        reflected = -rects[:, [2, 3, 0, 1]]
        self.assertEqual(set(map(tuple, rects)), set(map(tuple, reflected)))
        self.assertLess(len(rects), 7200)
        self.assertTrue(np.all(rects[1:, 0] >= rects[:-1, 2]))

    def test_nonuniform_integer_edges_remain_disjoint(self):
        rects = circle_union_rects(101, 73, 5)
        self.assertEqual(rects.dtype, np.dtype("int64"))
        self.assertTrue(np.all(rects[:, 2:] > rects[:, :2]))
        self.assertTrue(np.all(rects[1:, 0] >= rects[:-1, 2]))
        # Independent one-nanometre samples check exact rectangle overlap even
        # when the requested dimensions are not multiples of the raster step.
        xx, yy = np.meshgrid(np.arange(-87, 87) + .5, np.arange(-51, 51) + .5)
        cover = np.zeros_like(xx, dtype=np.uint8)
        for x1, y1, x2, y2 in rects:
            cover += (xx >= x1) & (xx < x2) & (yy >= y1) & (yy < y2)
        self.assertLessEqual(cover.max(), 1)

    def test_invalid_parameters(self):
        for args in ((0,), (-1,), (math.nan,), (100, -1), (100, math.inf),
                     (100, 0, 0), (100, 0, .5), (100, 0, 1.5)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                circle_union_rects(*args)


if __name__ == "__main__":
    unittest.main()
