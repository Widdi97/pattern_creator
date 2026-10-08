"""Small direct-geometry example; run as python -m examples.export_gds."""

import argparse
from pathlib import Path

from pattern_creator_export.direct import DirectLattice, DirectPattern, ShapeSpec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="directory for the two GDS examples")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    ring = DirectPattern(20000, 20000, 100, pattern_name="RING")
    ring.add_parametrized_shape("circle", 10000, 10000, 5000, boolean_operation="add")
    # Subtraction is an explicit operation; nested GDS boundaries alone are filled.
    ring.add_parametrized_shape("circle", 10000, 10000, 4000, boolean_operation="subtract")
    ring.export_gds(args.output / "ring.gds")

    lattice = DirectLattice(
        (2000, 0), (0, 2000), 10000, 8000, 100,
        [ShapeSpec("circle", (0, 0, 500), "add")], [(0, 0)],
        pattern_name="LATTICE",
    )
    # The top cell references bulk, four borders and four corners separately.
    lattice.export_gds(args.output / "lattice.gds")
    print(f"Wrote ring.gds and lattice.gds to {args.output.resolve()}")


if __name__ == "__main__":
    main()
