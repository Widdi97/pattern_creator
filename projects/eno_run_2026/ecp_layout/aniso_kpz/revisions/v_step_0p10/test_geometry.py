"""Finite-array correctness checks independent of the production tile builder."""
import unittest

import numpy as np

from geometry import ROLES, build_device


def record(rx=.02, ry=.015, ax=.06, ay=.05, angle=0):
    return {"lattice_a1_um": [ax, 0], "lattice_a2_um": [0, ay],
            "basis_centers_um": [[0.0, 0.0]], "major_semiaxis_um": rx,
            "minor_semiaxis_um": ry, "rotation_deg_ccw": angle}


def expanded(dev):
    rects = []
    for _, base, repeat in dev["structures"]:
        ax, ay, nx, ny = repeat or (0, 0, 1, 1)
        for i in range(nx):
            for j in range(ny):
                rects.extend(base + np.array([i * ax, j * ay] * 2))
    return np.asarray(rects, dtype=np.int64)


def covered(points, rects):
    return ((points[:, None, 0] >= rects[None, :, 0])
            & (points[:, None, 0] < rects[None, :, 2])
            & (points[:, None, 1] >= rects[None, :, 1])
            & (points[:, None, 1] < rects[None, :, 3])).sum(axis=1)


class GeometryTests(unittest.TestCase):
    def test_implicit_union_matches_all_pixel_centers_without_double_exposure(self):
        # Small finite patches, 1 nm sampling: every output pixel is checked
        # against an independently evaluated union of ALL finite-array mesas.
        for source in (record(), record(rx=.035), record(rx=.035, angle=90)):
            dev = build_device(source, size_nm=220, pixel_nm=1)
            rects = expanded(dev)
            lo = rects[:, :2].min(0) - 2
            hi = rects[:, 2:].max(0) + 2
            x, y = np.meshgrid(np.arange(lo[0], hi[0]) + .5, np.arange(lo[1], hi[1]) + .5)
            points = np.column_stack([x.ravel(), y.ravel()])
            inside = np.zeros(len(points), bool)
            hx, hy = dev["halfwidths_nm"]
            for i in range(dev["nx"]):
                for j in range(dev["ny"]):
                    inside |= (((points[:, 0] - i * dev["ax_nm"]) / hx) ** 2
                               + ((points[:, 1] - j * dev["ay_nm"]) / hy) ** 2 <= 1)
            counts = np.concatenate([covered(p, rects) for p in np.array_split(points, 30)])
            np.testing.assert_array_equal(counts, inside.astype(int))

    def test_nine_roles_counts_bbox_and_area(self):
        dev = build_device(record(), size_nm=220, pixel_nm=5)
        self.assertEqual([s[0] for s in dev["structures"]], list(ROLES))
        self.assertEqual((dev["nx"], dev["ny"]), (4, 4))
        self.assertTrue(all(len(rects) for _, rects, _ in dev["structures"]))
        rects = expanded(dev)
        area = np.prod(rects[:, 2:] - rects[:, :2], axis=1).sum()
        self.assertEqual(area, dev["exposed_area_nm2"])
        self.assertTrue(np.all(np.subtract(dev["analytic_bbox_nm"][2:], dev["analytic_bbox_nm"][:2]) <= 220))
        for role, rects, _ in dev["structures"]:
            box = dev["role_boxes_nm"][role]
            self.assertTrue(np.all(rects[:, :2] >= box[:2]))
            self.assertTrue(np.all(rects[:, 2:] <= box[2:]))

    def test_rotation_and_reflection(self):
        a = build_device(record(ax=.06, ay=.06), size_nm=220, pixel_nm=5)
        b = build_device(record(ax=.06, ay=.06, angle=90), size_nm=220, pixel_nm=5)
        ra, rb = expanded(a), expanded(b)
        points = np.array([[x + .5, y + .5] for x in range(-30, 220) for y in range(-30, 220)])
        def occupancy(p, r):
            return np.concatenate([covered(chunk, r) for chunk in np.array_split(p, 40)])
        np.testing.assert_array_equal(occupancy(points, ra), occupancy(points[:, ::-1], rb))
        reflected = points.copy()
        reflected[:, 0] = (a["nx"] - 1) * a["ax_nm"] - reflected[:, 0]
        np.testing.assert_array_equal(occupancy(points, ra), occupancy(reflected, ra))

    def test_b4_and_a7_narrow_gaps_remain_open(self):
        for source, expected_gap in (
            (record(1.0062305898749055, .8049844718999243, 1.98, 1.62), 10.031056200151545),
            (record(1.285739087062379, 1.028591269649903, 2.53, 2.07), 12.817460700193628),
        ):
            dev = build_device(source, size_nm=10_000, pixel_nm=5)
            self.assertAlmostEqual(dev["ay_nm"] - 2 * dev["halfwidths_nm"][1], expected_gap)
            self.assertEqual(dev["written_centerline_gaps_nm"], [0, 10])
            # Inspect only one bulk base tile; the centerline gap must remain
            # empty and the midpoint to the overlapping x-neighbor must fill.
            base = dev["structures"][0][1]
            ax, ay = dev["ax_nm"], dev["ay_nm"]
            ys = np.linspace(1.5 * ay - 3, 1.5 * ay - .1, 7)
            self.assertTrue(np.all(covered(np.column_stack([np.full(len(ys), ax), ys]), base) == 0))
            self.assertEqual(covered(np.array([[1.5 * ax - .1, ay]]), base)[0], 1)

    def test_reject_coarse_raster_and_small_patch(self):
        with self.assertRaises(ValueError):
            build_device(record(), pixel_nm=25)
        with self.assertRaises(ValueError):
            build_device(record(), size_nm=50)


if __name__ == "__main__":
    unittest.main()
