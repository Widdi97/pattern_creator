"""Strict read-back for this job's ECP JEOL52V3.0 rectangle exports.

Usage: python verify_v30.py set_a.v30 --pat set_a.pat

Export the one-field CTL with ECP's JBX 8100 FS profile, 1000 um field.
The 500 um PAT field is centred at (250, 250) um within that field. This
known transform is checked explicitly; geometry is never aligned by its bbox.
Only the RECT/compaction-8 subset observed in the existing EnO export is read.
This checks encoded geometry and ranks, not machine calibration or the JDF.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct


RECT_WORDS = {0xFF00: 4, 0xFF01: 4, 0xFF06: 4, 0xFF07: 4,
              0xFF10: 8, 0xFF11: 8}
RECORD_BYTES = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def b4(words, at):
    # JEOL B4 stores its high 16-bit word first; each word is little endian.
    return (words[at] << 16) | words[at + 1]


def decode_v30(path, on_rectangle=None):
    """Validate records and return counts; optionally visit compressed RECTs.

    Callback arguments are (field_index, field_xy, position_xy, rect_xywh,
    shot_rank, repetition_px_py_nx_ny). No callback means no array expansion,
    which permits inexpensive inspection of a multi-million-shot native file.
    """
    raw = Path(path).read_bytes()
    require(len(raw) >= 2 * RECORD_BYTES and len(raw) % RECORD_BYTES == 0,
            "V30 is empty, truncated, or not a whole number of 4096-byte records")
    records = [struct.unpack_from('<2048H', raw, k)
               for k in range(0, len(raw), RECORD_BYTES)]
    w = records[0]
    require(raw[:2] == b'ID' and raw[26:36] == b'JEOL52V3.0',
            "Expected ID record and JEOL52V3.0 format")
    header = {
        'chip_size_nm': [b4(w, 35), b4(w, 37)],
        'field_size_nm': [b4(w, 39), b4(w, 41)],
        'position_set_area_nm': [b4(w, 43), b4(w, 45)],
        'units_per_um': list(w[58:61]), 'max_shot_rank': w[64],
        'tx_records': b4(w, 72), 'stored_rectangles': b4(w, 74),
        'expanded_rectangles': b4(w, 82), 'fields': b4(w, 98),
    }
    require(header['units_per_um'] == [1000, 1000, 1000],
            "Expected 1 nm chip, position-set, and pattern units")
    require(all(v > 0 for v in header['chip_size_nm'] + header['field_size_nm']),
            "Invalid chip/field size")
    require(all(b4(w, k) == 0 for k in (66, 68, 70, 76, 78, 80, 84, 86, 88, 96)),
            "Only TX rectangle data without libraries/trapezoids/high counters is supported")
    require(header['tx_records'] == len(records) - 1, "TX record count mismatch")
    require(0 <= header['max_shot_rank'] <= 63, "Invalid maximum shot rank")
    fields, current, position, rank, compaction = [], None, None, None, None
    chip_ended = False
    stored, expanded = 0, 0
    for record_number, rec in enumerate(records[1:], 1):
        context = f'TX record {record_number}'
        require(not chip_ended, f'{context}: record after chip end')
        require(rec[0] == 0x5854, f'{context}: unsupported record type')
        # TX blocks form a chain: the header length reaches a field/chip/record
        # terminator; field/chip terminators carry the next block's length.
        boundary, boundaries = 2, {}
        for _ in range(rec[1]):
            length = rec[boundary]
            require(length > 0 and boundary + length < 2048,
                    f'{context}: invalid block length')
            boundary += length
            opcode = rec[boundary]
            require(opcode in (0xFFF2, 0xFFF4, 0xFFF5),
                    f'{context}: block does not end at a terminator')
            boundaries[boundary] = opcode
            if opcode == 0xFFF2:
                break
            boundary += 1
        require(len(boundaries) == rec[1] and boundaries.get(boundary) == 0xFFF2,
                f'{context}: block count or record terminator mismatch')
        end = boundary
        require(not any(rec[end + 1:]), f'{context}: nonzero data after record end')
        index, repeated_opcode = 3, None
        while index <= end:
            opcode = rec[index]
            if index in boundaries:
                require(opcode == boundaries[index], f'{context}: bad block terminator')
                require(compaction is None, f'{context}: unfinished compaction at block end')
                if opcode == 0xFFF2:
                    require(index == end, f'{context}: premature record end')
                    break
                require(current is not None, f'{context}: field end outside a field')
                current = None
                position, rank, repeated_opcode = None, None, None
                if opcode == 0xFFF5:
                    require(not chip_ended, f'{context}: repeated chip end')
                    chip_ended = True
                index += 2  # Skip the next block's length word.
                continue
            require(not chip_ended, f'{context}: data after chip end')
            if opcode in RECT_WORDS:
                repeated_opcode = opcode
                count = RECT_WORDS[opcode]
                start = index + 1
            elif opcode < 0xFF00 and repeated_opcode is not None:
                count = RECT_WORDS[repeated_opcode]
                start = index
            else:
                repeated_opcode = None
                count = {0xFFF0: 4, 0xFFF1: 4, 0xFF05: 1, 0xFFE8: 7}.get(opcode)
                require(count is not None, f'{context}: unknown/unsupported command {opcode:#06x}')
                start = index + 1
                require(start + count <= end and not any(start <= p < start + count for p in boundaries),
                        f'{context}: truncated command')
                require(compaction is None, f'{context}: interrupted compaction')
                if opcode == 0xFFF0:
                    require(current is None, f'{context}: new field before previous field ended')
                    current = {'origin_nm': [b4(rec, start), b4(rec, start + 2)],
                               'stored_rectangles': 0, 'expanded_rectangles': 0,
                               'shot_ranks': Counter(), 'position_sets_nm': set()}
                    fields.append(current)
                    position, rank = None, None
                else:
                    require(current is not None, f'{context}: command outside field')
                    if opcode == 0xFFF1:
                        position = (b4(rec, start), b4(rec, start + 2))
                        current['position_sets_nm'].add(position)
                    elif opcode == 0xFF05:
                        rank = rec[start]
                        require(rank <= header['max_shot_rank'], f'{context}: rank exceeds ID maximum')
                    else:
                        npt, lx, ly, nx, ny = (rec[start], b4(rec, start + 1),
                                               b4(rec, start + 3), rec[start + 5], rec[start + 6])
                        require(npt > 0 and nx > 0 and ny > 0, f'{context}: zero compaction count')
                        require((nx > 1 and lx > 0 and lx % (nx - 1) == 0) or (nx == 1 and lx == 0),
                                f'{context}: invalid X compaction length/pitch')
                        require((ny > 1 and ly > 0 and ly % (ny - 1) == 0) or (ny == 1 and ly == 0),
                                f'{context}: invalid Y compaction length/pitch')
                        compaction = [npt, lx // (nx - 1) if nx > 1 else 0,
                                      ly // (ny - 1) if ny > 1 else 0, nx, ny]
                index = start + count
                continue
            require(start + count <= end and not any(start <= p < start + count for p in boundaries),
                    f'{context}: truncated rectangle')
            require(current is not None and position is not None and rank is not None,
                    f'{context}: rectangle without explicit field/position/rank')
            values = tuple(b4(rec, k) for k in range(start, start + 8, 2)) if count == 8 else rec[start:start + 4]
            x, y, width, height = values
            require(width > 0 and height > 0, f'{context}: zero-area rectangle')
            repeat = tuple(compaction[1:]) if compaction else (0, 0, 1, 1)
            px, py, nx, ny = repeat
            require(position[0] + x + width + px * (nx - 1) <= header['field_size_nm'][0]
                    and position[1] + y + height + py * (ny - 1) <= header['field_size_nm'][1],
                    f'{context}: geometry exceeds field')
            copies = nx * ny
            stored += 1
            expanded += copies
            current['stored_rectangles'] += 1
            current['expanded_rectangles'] += copies
            current['shot_ranks'][rank] += copies
            if on_rectangle:
                on_rectangle(len(fields) - 1, current['origin_nm'], position, values, rank, repeat)
            if compaction:
                compaction[0] -= 1
                if compaction[0] == 0:
                    compaction = None
            index = start + count
    require(chip_ended and current is None, 'Missing chip end or unterminated field')
    require(len(fields) == header['fields'] and stored == header['stored_rectangles']
            and expanded == header['expanded_rectangles'], 'ID field/rectangle counts do not match decoded data')
    for field in fields:
        field['shot_ranks'] = dict(field['shot_ranks'])
        field['position_sets_nm'] = sorted(map(list, field['position_sets_nm']))
    return {'header': header, 'fields': fields}


def expected_rectangles(path):
    """Read only this job's positive RECT PAT, preserving array multiplicity."""
    result, names = Counter(), set()
    current = None
    for number, raw in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(';'):
            continue
        opcode, _, tail = line.partition(' ')
        context = f'PAT line {number}'
        if opcode == 'D':
            parts = [v.strip() for v in tail.split(',')]
            require(current is None and len(parts) in (1, 5) and parts[0] and parts[0] not in names,
                    f'{context}: invalid/duplicate D definition')
            names.add(parts[0])
            current = {'name': parts[0], 'I': None, 'C': None, 'rects': []}
            repeat = tuple(map(int, parts[1:])) if len(parts) == 5 else (0, 0, 1, 1)
            px, py, nx, ny = repeat
            require(nx > 0 and ny > 0 and (nx == 1 or px > 0) and (ny == 1 or py > 0),
                    f'{context}: invalid repetition')
        elif opcode in ('I', 'C'):
            require(current is not None and current[opcode] is None and not current['rects'],
                    f'{context}: misplaced exposure metadata')
            current[opcode] = int(tail)
        elif opcode == 'RECT':
            require(current is not None, f'{context}: rectangle outside a definition')
            values = tuple(map(int, tail.split(',')))
            require(len(values) == 4 and values[0] < values[2] and values[1] < values[3],
                    f'{context}: invalid rectangle')
            current['rects'].append(values)
        elif opcode == 'END':
            require(current is not None and not tail and current['I'] == 16 and current['C'] == 100,
                    f'{context}: expected complete I16/C100 definition')
            for x1, y1, x2, y2 in current['rects']:
                for iy in range(ny):
                    for ix in range(nx):
                        rect = (x1 + ix * px, y1 + iy * py, x2 + ix * px, y2 + iy * py)
                        require(min(rect) >= 0 and max(rect) <= 500000, f'{context}: outside 500 um PAT field')
                        result[rect] += 1
            current = None
        else:
            raise ValueError(f'{context}: unsupported statement {opcode!r}')
    require(current is None and result, 'Incomplete or empty PAT')
    require(max(result.values()) == 1, 'PAT contains duplicate exposure rectangles')
    return result, len(names)


def verify(v30_path, pat_path):
    """Return JSONable exact-match evidence; raise ValueError for any mismatch."""
    expected, n_definitions = expected_rectangles(pat_path)
    expected_count, extra, first_extra = sum(expected.values()), 0, []

    def compare(field_index, field, position, values, rank, repetition):
        nonlocal extra
        require(field_index == 0 and field == [0, 0], 'Expected exactly one field at chip origin')
        require(position == (250000, 250000), 'Expected the explicit 250 um ECP centring offset')
        require(rank == 0, 'Expected shot rank 0 for all I16/C100 geometry')
        x, y, width, height = values
        px, py, nx, ny = repetition
        for iy in range(ny):
            for ix in range(nx):
                # JEOL chip Y points down. Header chip size is checked below;
                # this fixed transform preserves absolute PAT placement.
                ax = field[0] + position[0] + x + ix * px - 250000
                ay = 1000000 - (field[1] + position[1] + y + iy * py + height) - 250000
                rect = (ax, ay, ax + width, ay + height)
                if expected.get(rect, 0):
                    expected[rect] -= 1
                else:
                    extra += 1
                    if len(first_extra) < 3:
                        first_extra.append(rect)

    evidence = decode_v30(v30_path, compare)
    header = evidence['header']
    require(header['fields'] == 1 and len(evidence['fields']) == 1, 'Expected exactly one write field')
    require(header['chip_size_nm'] == header['field_size_nm'] == header['position_set_area_nm'] == [1000000, 1000000],
            'Expected one 1000 um JEOL field/chip/position-set area')
    require(header['max_shot_rank'] == 0, 'Expected maximum shot rank 0')
    require(evidence['fields'][0]['position_sets_nm'] == [[250000, 250000]],
            'Expected only the centred 250 um position-set offset')
    missing = sum(expected.values())
    require(missing == extra == 0, f'Rectangle mismatch: missing={missing}, extra={extra}, first_extra={first_extra}')
    evidence.update({'result': 'exact RECT multiset and rank match',
                     'expected_rectangles': expected_count, 'pat_definitions': n_definitions,
                     'missing': missing, 'extra': extra,
                     'coordinate_transform': 'JEOL Y-down; 1000000 nm chip height; subtract fixed 250000 nm XY centring offset; no fitted translation',
                     'v30_sha256': hashlib.sha256(Path(v30_path).read_bytes()).hexdigest(),
                     'pat_sha256': hashlib.sha256(Path(pat_path).read_bytes()).hexdigest()})
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('v30', type=Path)
    parser.add_argument('--pat', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.v30, args.pat), indent=2))
