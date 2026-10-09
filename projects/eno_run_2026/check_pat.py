"""Independent check of a written .pat file: re-read RECTs (expanding D-line
repetition), rasterise each device, count connected pillars and report
equivalent diameters. Structures named '<device>_bNN' are analysed together.

usage: python check_pat.py <file.pat> [pixel_nm]
"""
import re
import sys
from collections import defaultdict

import numpy as np
from scipy import ndimage


def read_pat(path, expand=True):
    structs, name, rects, rep = {}, None, [], None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("D "):
                head = [v.strip() for v in line[2:].split(",")]
                name, rects = head[0], []
                rep = [int(v) for v in head[1:]] if len(head) == 5 else None
            elif line.startswith("RECT"):
                rects.append([int(v) for v in line[4:].split(",")])
            elif line == "END" and name is not None:
                r = np.array(rects, dtype=np.int64)
                if expand and rep is not None:
                    px, py, nx, ny = rep
                    sh = np.array([[i * px, j * py, i * px, j * py] for j in range(ny) for i in range(nx)])
                    r = (r[None] + sh[:, None]).reshape(-1, 4)
                structs[name] = r
                name = None
    return structs


def read_pat_raw(path):
    """name -> (rects, repeat or None) without expanding the D-line repetition."""
    structs, name, rects, rep = {}, None, [], None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("D "):
                head = [v.strip() for v in line[2:].split(",")]
                name, rects = head[0], []
                rep = tuple(int(v) for v in head[1:]) if len(head) == 5 else None
            elif line.startswith("RECT"):
                rects.append([int(v) for v in line[4:].split(",")])
            elif line == "END" and name is not None:
                if rects:  # empty structures expose nothing
                    structs[name] = (np.array(rects, dtype=np.int64), rep)
                name = None
    return structs


def overlap_area(A, B, same=False):
    """Exact total overlap area (nm^2) between two rect sets (touching edges do not count)."""
    w = np.minimum(A[:, None, 2], B[None, :, 2]) - np.maximum(A[:, None, 0], B[None, :, 0])
    h = np.minimum(A[:, None, 3], B[None, :, 3]) - np.maximum(A[:, None, 1], B[None, :, 1])
    ov = np.clip(w, 0, None) * np.clip(h, 0, None)
    if same:
        ov = np.triu(ov, 1)
    return int(ov.sum())


def double_exposure(path):
    """Exact check that no area of the pattern file is exposed twice.

    Returns a list of (structure_a, structure_b, overlap_nm2); empty = clean.
    Checks rects inside each structure, all repeated copies against each other
    and every structure instance against every other one (bbox sweep + exact test).
    """
    raw = read_pat_raw(path)
    problems = []
    inst_rects, inst_box, inst_name = [], [], []
    for name, (rects, rep) in raw.items():
        for start in range(0, len(rects), 400):  # within-structure pairs, chunked
            for start2 in range(start, len(rects), 400):
                a, b = rects[start:start + 400], rects[start2:start2 + 400]
                ov = overlap_area(a, b, same=True) if start == start2 else overlap_area(a, b)
                if ov:
                    problems.append((name, name, ov))
        px, py, nx, ny = rep if rep else (0, 0, 1, 1)
        box = np.array([rects[:, 0].min(), rects[:, 1].min(), rects[:, 2].max(), rects[:, 3].max()])
        for j in range(ny):
            for i in range(nx):
                off = np.array([i * px, j * py, i * px, j * py])
                inst_rects.append((name, off))
                inst_box.append(box + off)
                inst_name.append(name)
    boxes = np.array(inst_box)
    order = np.argsort(boxes[:, 0])
    boxes, inst_rects = boxes[order], [inst_rects[k] for k in order]
    for k in range(len(boxes)):
        hi = np.searchsorted(boxes[:, 0], boxes[k, 2], side="left")
        cand = np.arange(k + 1, hi)
        cand = cand[(boxes[cand, 1] < boxes[k, 3]) & (boxes[cand, 3] > boxes[k, 1])
                    & (boxes[cand, 2] > boxes[k, 0])]
        if cand.size == 0:
            continue
        na, oa = inst_rects[k]
        A = raw[na][0] + oa
        for c in cand:
            nb, ob = inst_rects[c]
            B = raw[nb][0] + ob
            lo = np.maximum(boxes[k, :2], boxes[c, :2])
            up = np.minimum(boxes[k, 2:], boxes[c, 2:])
            sa = A[(A[:, 2] > lo[0]) & (A[:, 0] < up[0]) & (A[:, 3] > lo[1]) & (A[:, 1] < up[1])]
            sb = B[(B[:, 2] > lo[0]) & (B[:, 0] < up[0]) & (B[:, 3] > lo[1]) & (B[:, 1] < up[1])]
            if len(sa) and len(sb):
                ov = overlap_area(sa, sb)
                if ov:
                    problems.append((na, nb, ov))
    return problems, len(boxes)


def analyse(rects, pixel):
    x0, y0 = rects[:, 0].min(), rects[:, 1].min()
    nx = (rects[:, 2].max() - x0) // pixel + 2
    ny = (rects[:, 3].max() - y0) // pixel + 2
    m = np.zeros((ny, nx), dtype=np.int32)
    for a, b, c, d in rects:
        m[(b - y0) // pixel:(d - y0) // pixel, (a - x0) // pixel:(c - x0) // pixel] += 1
    lab, n = ndimage.label(m > 0)  # 4-connectivity: diagonal pixel contact does not join
    areas = ndimage.sum(m > 0, lab, np.arange(1, n + 1)) * pixel ** 2
    return n, int(m.max()), 2 * np.sqrt(areas / np.pi)


if __name__ == "__main__":
    pixel = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    problems, n_inst = double_exposure(sys.argv[1])
    print(f"double-exposure check: {n_inst} structure instances, "
          + ("NO overlapping exposure" if not problems else f"{len(problems)} OVERLAPS"))
    for a, b, ov in problems[:20]:
        print(f"   overlap {ov} nm^2 between {a} and {b}")
    devices = defaultdict(list)
    for name, rects in read_pat(sys.argv[1]).items():
        if not name.endswith("labels"):
            devices[re.sub(r"(_[bd]\d+|_x_-?\d_y_-?\d)$", "", name)].append(rects)
    for dev, parts in devices.items():
        rects = np.concatenate(parts)
        n, overlap, deq = analyse(rects, pixel)
        print(f"{dev:<44} structures {len(parts):3d}  components {n:5d}  max cover {overlap}  "
              f"d_eq median {np.median(deq):8.1f} nm  min {deq.min():8.1f}  max {deq.max():8.1f}")


