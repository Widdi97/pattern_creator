"""Double-exposure check of a chip field together with its chip x/y numbers.

The numbers come from a separate pat/ctl, so check_pat.py alone cannot see them.
This combines the chip structures with a representative set of number glyphs
(1- and 2-digit x and y labels; only one x and one y label at a time, as written)
and runs the exact overlap check on each combination.

usage: python check_with_numbers.py <chip.pat> <numbers.pat>
"""
import os
import sys
import tempfile

from check_pat import double_exposure


def block(text, name):
    start = text.index(f"D {name}\n")
    return text[start:text.index("END", start) + 3] + "\n"


def numbers_as_rect(text):
    # numbers use the numeric shape code 'P 0, x1, y1, x2, y2' (= RECT); convert for the checker
    return "\n".join("RECT" + ln[4:] if ln.startswith("P 0,") else ln for ln in text.splitlines()) + "\n"


if __name__ == "__main__":
    chip = open(sys.argv[1]).read()
    nums = open(sys.argv[2]).read()
    bad = 0
    for nx, ny in ((1, 1), (8, 98), (98, 8), (49, 50)):
        combo = chip + numbers_as_rect(block(nums, f"nbr_x_{nx}") + block(nums, f"nbr_y_{ny}"))
        with tempfile.NamedTemporaryFile("w", suffix=".pat", delete=False) as f:
            f.write(combo)
        problems, n = double_exposure(f.name)
        os.unlink(f.name)
        print(f"chip + nbr_x_{nx} + nbr_y_{ny}: {n} instances, "
              + ("no overlapping exposure" if not problems else f"{len(problems)} OVERLAPS {problems[:3]}"))
        bad += len(problems)
    sys.exit(1 if bad else 0)

