import struct
import unittest

from font_name_inspector import _parse_cmap4, _parse_cmap12_or_13


def make_format4(end_codes, start_codes, deltas, range_offsets, glyph_array=b""):
    count = len(end_codes)
    seg_count_x2 = count * 2
    length = 16 + count * 8 + len(glyph_array)
    header = struct.pack(">7H", 4, length, 0, seg_count_x2, 4, 1, 0)
    arrays = (
        struct.pack(f">{count}H", *end_codes)
        + b"\x00\x00"
        + struct.pack(f">{count}H", *start_codes)
        + struct.pack(f">{count}H", *deltas)
        + struct.pack(f">{count}H", *range_offsets)
    )
    return header + arrays + glyph_array


class CmapRecoveryTests(unittest.TestCase):
    def test_format4_valid_bmp_character(self):
        data = make_format4(
            end_codes=[0x0041, 0xFFFF],
            start_codes=[0x0041, 0xFFFF],
            deltas=[1, 1],
            range_offsets=[0, 0],
        )
        codepoints, warnings = _parse_cmap4(data, glyph_count=128)
        self.assertEqual(codepoints, {0x0041})
        self.assertEqual(warnings, [])

    def test_format4_bad_segment_is_skipped_not_fatal(self):
        data = make_format4(
            end_codes=[0x0041, 0xFFFF],
            start_codes=[0x0041, 0xFFFF],
            deltas=[0, 1],
            range_offsets=[2, 0],
        )
        codepoints, warnings = _parse_cmap4(data, glyph_count=128)
        self.assertEqual(codepoints, set())
        self.assertTrue(warnings)
        self.assertIn("skipped", warnings[0])

    def test_format12_ignores_four_byte_trailer(self):
        expected = struct.pack(">HHLLL", 12, 0, 28, 0, 1)
        group = struct.pack(">LLL", 0x4E00, 0x4E02, 10)
        data = expected + group + b"\x00\x00\x00\x00"
        codepoints, warnings = _parse_cmap12_or_13(data, 12, glyph_count=100)
        self.assertEqual(codepoints, {0x4E00, 0x4E01, 0x4E02})
        self.assertTrue(any("trailing padding" in item for item in warnings))

    def test_format12_clamps_out_of_range_glyph_ids(self):
        data = struct.pack(">HHLLL", 12, 0, 28, 0, 1)
        data += struct.pack(">LLL", 0x4E00, 0x4E05, 98)
        codepoints, _ = _parse_cmap12_or_13(data, 12, glyph_count=100)
        self.assertEqual(codepoints, {0x4E00, 0x4E01})

    def test_format13_constant_glyph(self):
        data = struct.pack(">HHLLL", 13, 0, 28, 0, 1)
        data += struct.pack(">LLL", 0x4E00, 0x4E02, 5)
        codepoints, warnings = _parse_cmap12_or_13(data, 13, glyph_count=100)
        self.assertEqual(codepoints, {0x4E00, 0x4E01, 0x4E02})
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
