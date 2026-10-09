"""Reader for JEOL52 V3.0 (.v30) pattern data as exported by ECP (spec: ECP/JEOL_V52_Data_Format.pdf).

On disk: records of 2048 words (4096 bytes); words little-endian (B2); 4-byte integers
(B4) are stored high word first; ASCII as written. Records: ID, CM, MP, LB, TX.

usage: python read_v30.py <file.v30> [--dump N]
"""
import sys
from collections import Counter

import numpy as np

REC_WORDS = 2048

GEOM = {  # command: (name, kind, words of data)
    0xFF00: ("XS-rect", "rect", 4), 0xFF01: ("YS-rect", "rect", 4),
    0xFF06: ("XL-rect", "rect", 4), 0xFF07: ("YL-rect", "rect", 4),
    0xFF10: ("XLL-rect", "rect4", 8), 0xFF11: ("YLL-rect", "rect4", 8),
    0xFF02: ("XS-trap", "trap", 6), 0xFF03: ("YS-trap", "trap", 6),
    0xFF08: ("XL-trap", "trap", 6), 0xFF09: ("YL-trap", "trap", 6),
    0xFF12: ("XLL-trap", "trap4", 12), 0xFF13: ("YLL-trap", "trap4", 12),
}


def b4(w, i):
    return (int(w[i]) << 16) | int(w[i + 1])


def ascii_words(w, i, n):
    return b"".join(int(x).to_bytes(2, "little") for x in w[i:i + n]).decode("latin1")


def read_id(w):
    return {
        "id_name": ascii_words(w, 1, 12).strip(), "format": ascii_words(w, 13, 5),
        "date": ascii_words(w, 19, 8), "chip_size": (b4(w, 35), b4(w, 37)),
        "field_size": (b4(w, 39), b4(w, 41)), "position_set_area": (b4(w, 43), b4(w, 45)),
        "unit_chip": int(w[58]), "unit_position_set": int(w[59]), "unit_pattern": int(w[60]),
        "max_shot_rank": int(w[64]),
        "n_records": {"CM": b4(w, 66), "MP": b4(w, 68), "LB": b4(w, 70), "TX": b4(w, 72)},
        "n_rect_L": b4(w, 74), "n_trap_L": b4(w, 76), "n_rect_decompacted_L": b4(w, 82),
        "n_trap_decompacted_L": b4(w, 84), "n_libblocks": b4(w, 96), "n_textblocks": b4(w, 98),
    }


def records(path):
    raw = open(path, "rb").read()
    w = np.frombuffer(raw[: len(raw) // 2 * 2], dtype="<u2")
    n = len(w) // REC_WORDS
    return [w[k * REC_WORDS:(k + 1) * REC_WORDS] for k in range(n)], len(raw)


def scan_commands(rec, start=3):
    """Walk a TX/LB record. Returns (list of events, unknown words). Tracks command omission."""
    events, i, current = [], start, None
    while i < len(rec):
        c = int(rec[i])
        if c == 0xFFF2:  # record end
            events.append(("record_end", i))
            break
        if c in GEOM:
            current = c
            name, kind, n = GEOM[c]
            events.append((name, rec[i + 1:i + 1 + n].copy()))
            i += 1 + n
            continue
        if c == 0xFFF0:
            events.append(("field", (b4(rec, i + 1), b4(rec, i + 3)))); i += 5; current = None; continue
        if c == 0xFFF1:
            events.append(("position_set", (b4(rec, i + 1), b4(rec, i + 3)))); i += 5; current = None; continue
        if c == 0xFF05:
            events.append(("shot_rank", int(rec[i + 1]))); i += 2; current = None; continue
        if c in (0xFFF4, 0xFFF5):
            events.append(("field_end" if c == 0xFFF4 else "chip_end", int(rec[i + 1]))); i += 2; current = None
            continue
        if c == 0xFFE8:
            events.append(("compaction8", (int(rec[i + 1]), b4(rec, i + 2), b4(rec, i + 4), int(rec[i + 6]), int(rec[i + 7]))))
            i += 8; current = None; continue
        if c >= 0xFF00 and current is None:
            events.append(("UNKNOWN", hex(c), i)); i += 1; continue
        if current is not None:  # omitted command: same geometry again
            name, kind, n = GEOM[current]
            events.append((name, rec[i:i + n].copy()))
            i += n
            continue
        events.append(("UNKNOWN", hex(c), i)); i += 1
    return events


if __name__ == "__main__":
    recs, nbytes = records(sys.argv[1])
    head = read_id(recs[0])
    for k, v in head.items():
        print(f"{k:24} {v}")
    kinds = Counter(ascii_words(r, 0, 1) for r in recs)
    print("record identifiers:", dict(kinds), "bytes", nbytes)
    allc = Counter()
    for r in recs[1:]:
        ident = ascii_words(r, 0, 1)
        if ident not in ("TX", "LB"):
            continue
        ev = scan_commands(r)
        allc.update(e[0] for e in ev)
    print("events:", dict(allc))
