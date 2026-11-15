import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from ass_font_audit import parse_ass_text


SAMPLE_ASS = r"""[Script Info]
Title: minimal test

[V4+ Styles]
Format: Name, Fontname, Fontsize
Style: Default,Main Sans,48
Style: OP,Song Face,42
Style: Unused,Unused Face,30

[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0,0:00:01.00,0:00:02.00,Default,{\\fnInline Script Face}Hello
Dialogue: 0,0:00:03.00,0:00:04.00,Default,Normal dialogue
Comment: 0,0:00:04.00,0:00:05.00,OP,ignored comment
"""


class AssFontAuditTests(unittest.TestCase):
    def test_active_styles_inline_overrides_and_unused_styles(self):
        result = parse_ass_text(SAMPLE_ASS, "sample.ass")
        fonts = {row["font_name"]: row for row in result["fonts"]}

        self.assertEqual(result["dialogue_event_count"], 2)
        self.assertEqual(result["comment_event_count"], 1)
        self.assertEqual(fonts["Main Sans"]["dialogue_style_events"], 2)
        self.assertEqual(fonts["Inline Script Face"]["inline_fn_occurrences"], 1)
        self.assertIn("Unused", result["unused_style_names"])
        self.assertNotIn("OP", result["active_style_event_counts"])

    def test_metadata_is_retained(self):
        result = parse_ass_text(SAMPLE_ASS, "sample.ass")
        self.assertEqual(result["script_info"]["Title"], "minimal test")


if __name__ == "__main__":
    unittest.main()
