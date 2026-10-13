"""In-memory JEOL decoder fixtures; no fabricated V30 deliverables are written.

Run with: python -m unittest test_v30
"""

import json
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

import verify_v30


PAT = ('D TEST, 1000, 2000, 3, 2\nI 16\nC 100\n'
       'RECT 100000,100000,100025,100275\nEND\n')
PAT_TWO = PAT.replace('END', 'RECT 100100,100000,100125,100275\nEND')


def b4(value):
    return [value >> 16, value & 65535]


def fixture(two_rectangles=False, duplicate=False):
    """Minimal synthetic ID/TX records using the decoder's documented subset.

    The 3x2 array covers the same PAT rectangle at positive X/Y pitches.
    JEOL Y points down, so its first row represents the PAT array's top row.
    The optional second rectangle deliberately omits the repeated opcode.
    """
    count = 2 if two_rectangles else 1
    header = [0] * 2048
    header[0] = 0x4449
    header[13:18] = struct.unpack('<5H', b'JEOL52V3.0')
    for at in (35, 37, 39, 41, 43, 45):
        header[at:at + 2] = b4(1000000)
    header[58:61] = [1000] * 3
    for at, value in ((72, 1), (74, count), (82, 6 * count), (98, 1)):
        header[at:at + 2] = b4(value)
    commands = [0xFFF0, *b4(0), *b4(0), 0xFF05, 0,
                0xFFF1, *b4(250000), *b4(250000),
                0xFFE8, count, *b4(2000), *b4(2000), 3, 2,
                0xFF11, *b4(100000), *b4(397725), *b4(25), *b4(275)]
    if two_rectangles:
        commands += [*b4(100000 if duplicate else 100100), *b4(397725),
                     *b4(25), *b4(275)]
    record = [0x5854, 2, len(commands) + 1] + commands + [0xFFF5, 1, 0xFFF2]
    record += [0] * (2048 - len(record))
    return struct.pack('<4096H', *(header + record))


def changed_word(raw, at, value):
    out = bytearray(raw)
    struct.pack_into('<H', out, at * 2, value)
    return bytes(out)


def verify_bytes(raw, pat=PAT):
    # Patch reads, rather than create a file that could be mistaken for a job.
    with patch.object(Path, 'read_bytes', return_value=raw), \
            patch.object(Path, 'read_text', return_value=pat):
        return verify_v30.verify('fixture.v30', 'fixture.pat')


class V30Tests(unittest.TestCase):
    def test_exact_array(self):
        evidence = verify_bytes(fixture())
        self.assertEqual(evidence['expected_rectangles'], 6)
        self.assertEqual(evidence['missing'], 0)
        self.assertEqual(evidence['extra'], 0)
        self.assertEqual(evidence['fields'][0]['shot_ranks'], {0: 6})
        self.assertIn('no fitted translation', evidence['coordinate_transform'])
        json.dumps(evidence)  # Evidence is safe to persist as JSON.

    def test_omitted_repeated_opcode(self):
        evidence = verify_bytes(fixture(two_rectangles=True), PAT_TWO)
        self.assertEqual(evidence['expected_rectangles'], 12)
        self.assertEqual(evidence['header']['stored_rectangles'], 2)

    def test_missing_and_duplicate_rectangles(self):
        with self.assertRaisesRegex(ValueError, 'missing=6, extra=0'):
            verify_bytes(fixture(), PAT_TWO)
        with self.assertRaisesRegex(ValueError, 'missing=0, extra=6'):
            verify_bytes(fixture(two_rectangles=True, duplicate=True))

    def test_corrupt_streams(self):
        raw = fixture()
        cases = {
            'truncated byte': raw[:-1],
            'truncated whole record': raw[:-4096],
            'wrong units': changed_word(raw, 58, 999),
            'unknown command': changed_word(raw, 2051, 0xFF88),
            'unsupported trapezoid': changed_word(raw, 2071, 0xFF12),
            'unsupported compaction': changed_word(raw, 2063, 0xFFE9),
            'wrong shot rank': changed_word(raw, 2057, 1),
            'wrong position': changed_word(raw, 2061, 1),
            'noninteger compaction pitch': changed_word(raw, 2066, 2001),
            'unfinished compaction': changed_word(raw, 2064, 2),
            'wrong field count': changed_word(raw, 99, 2),
            'wrong rectangle count': changed_word(raw, 83, 7),
            'wrong chip size': changed_word(raw, 36, 16961),
            'invalid block length': changed_word(raw, 2050, 65535),
            'unsupported record type': changed_word(raw, 2048, 0x424C),
            'nonzero record padding': changed_word(raw, 4095, 1),
            'missing chip end': changed_word(raw, 2080, 0xFFF4),
        }
        for name, data in cases.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify_bytes(data)

    def test_no_fitted_translation(self):
        # Shift both X coordinates consistently: equal shape and size must not
        # pass when its absolute placement differs from the requested PAT.
        shifted = PAT.replace('100000,100000,100025,100275',
                              '100001,100000,100026,100275')
        with self.assertRaisesRegex(ValueError, 'missing=6, extra=6'):
            verify_bytes(fixture(), shifted)

    def test_pat_must_match_job_contract(self):
        for text in (PAT.replace('I 16', 'I 15'), PAT.replace('C 100', 'C 122'),
                     PAT.replace('RECT', 'CIRCLE'), PAT.replace('END\n', ''),
                     PAT.replace('D TEST,', 'D ,'), PAT + PAT):
            with self.subTest(text=text), self.assertRaises(ValueError):
                verify_bytes(fixture(), text)


if __name__ == '__main__':
    unittest.main()
