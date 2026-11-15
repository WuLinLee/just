#!/usr/bin/env python3
"""Extract ASS/SSA style fonts and inline font overrides using only Python stdlib.

This is a research helper, not a complete libass renderer. It reports declared
styles separately from styles used by Dialogue events and captures inline \\fn
and \\r overrides. It does not resolve Windows font fallback or embedded fonts
inside MKV/MKS containers.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


STYLE_SECTIONS = {"[v4+ styles]", "[v4 styles]"}
EVENT_SECTION = "[events]"
FONT_SECTION = "[fonts]"
BLOCK_RE = re.compile(r"\{([^}]*)\}")
FONT_TAG_RE = re.compile(r"\\fn([^\\}]*)")
RESET_TAG_RE = re.compile(r"\\r([^\\}]*)")
EMBEDDED_NAME_RE = re.compile(r"^\s*fontname\s*:\s*(.*?)\s*$", re.IGNORECASE)


def decode_ass(raw: bytes) -> tuple[str, str]:
    """Decode common ASS encodings while preserving a useful encoding label."""
    candidates = ("utf-8-sig", "utf-16", "gb18030", "cp932")
    for encoding in candidates:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8-replacement"


def split_record(payload: str, fields: list[str]) -> dict[str, str]:
    """Split a comma-separated ASS row while preserving commas in the last field."""
    values = payload.split(",", max(0, len(fields) - 1))
    values += [""] * max(0, len(fields) - len(values))
    return {name.strip().lower(): value.strip() for name, value in zip(fields, values)}


def style_role(style_name: str) -> str:
    """Best-effort label from the style name; never treat this as ground truth."""
    s = style_name.casefold().replace("_", " ").replace("-", " ")
    tokens = set(s.split())
    if "op" in tokens or s.startswith("op"):
        return "op_or_opening"
    if "ed" in tokens or s.startswith("ed"):
        return "ed_or_ending"
    if any(x in s for x in ("staff", "credit", "translator")):
        return "staff_or_credit"
    if any(x in s for x in ("title", "logo", "nexttitle")):
        return "title_or_logo"
    if any(x in s for x in ("screen", "sign", "note", "menu")):
        return "screen_sign_or_note"
    if any(x in s for x in ("annotation", "superscript", "ruby", "comment")):
        return "annotation_or_ruby"
    if any(x in tokens for x in ("cn", "zh", "chs", "cht")):
        return "chinese_style"
    if any(x in tokens for x in ("jp", "ja", "jpn")):
        return "japanese_style"
    if any(x in tokens for x in ("default", "main", "dialogue", "text")):
        return "dialogue_or_default"
    return "style_name_unspecified"


def parse_ass_text(text: str, source_name: str = "<memory>", sha256: str = "") -> dict[str, Any]:
    """Parse an ASS/SSA text file into style/event/font observations."""
    section = ""
    style_format: list[str] = []
    event_format: list[str] = []
    styles: dict[str, dict[str, str]] = {}
    dialogues: list[dict[str, str]] = []
    comment_event_count = 0
    embedded_fonts: list[str] = []
    script_info: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.casefold()
            continue

        if section == "[script info]" and ":" in line:
            key, value = line.split(":", 1)
            script_info[key.strip()] = value.strip()
            continue

        if section in STYLE_SECTIONS:
            if line.casefold().startswith("format:"):
                style_format = [x.strip() for x in line.split(":", 1)[1].split(",")]
            elif line.casefold().startswith("style:") and style_format:
                row = split_record(line.split(":", 1)[1].lstrip(), style_format)
                name = row.get("name", "")
                if name:
                    styles[name] = row
            continue

        if section == EVENT_SECTION:
            if line.casefold().startswith("format:"):
                event_format = [x.strip() for x in line.split(":", 1)[1].split(",")]
            elif line.casefold().startswith("dialogue:") and event_format:
                dialogues.append(split_record(line.split(":", 1)[1].lstrip(), event_format))
            elif line.casefold().startswith("comment:") and event_format:
                comment_event_count += 1
            continue

        if section == FONT_SECTION:
            m = EMBEDDED_NAME_RE.match(line)
            if m and m.group(1):
                embedded_fonts.append(m.group(1).strip())

    # Per-font statistics keep declared, active, inline and embedded evidence distinct.
    font_stats: dict[str, dict[str, Any]] = {}

    def touch(font_name: str) -> dict[str, Any] | None:
        font_name = font_name.strip()
        if not font_name:
            return None
        rec = font_stats.setdefault(
            font_name,
            {
                "font_name": font_name,
                "normalized_name_without_vertical_prefix": font_name.lstrip("@"),
                "style_definitions": 0,
                "dialogue_style_events": 0,
                "inline_fn_occurrences": 0,
                "reset_style_events": 0,
                "embedded_font_entries": 0,
                "styles": set(),
                "roles": set(),
                "source_kinds": set(),
            },
        )
        return rec

    for style_name, row in styles.items():
        font_name = row.get("fontname", "")
        rec = touch(font_name)
        if rec:
            rec["style_definitions"] += 1
            rec["styles"].add(style_name)
            rec["roles"].add(style_role(style_name))
            rec["source_kinds"].add("style_definition")

    active_style_counts: Counter[str] = Counter()
    inline_override_events: Counter[str] = Counter()
    reset_style_counts: Counter[str] = Counter()

    for event in dialogues:
        style_name = event.get("style", "")
        if style_name:
            active_style_counts[style_name] += 1
            row = styles.get(style_name)
            if row:
                rec = touch(row.get("fontname", ""))
                if rec:
                    rec["dialogue_style_events"] += 1
                    rec["styles"].add(style_name)
                    rec["roles"].add(style_role(style_name))
                    rec["source_kinds"].add("active_dialogue_style")

        event_text = event.get("text", "")
        for block in BLOCK_RE.findall(event_text):
            for match in FONT_TAG_RE.findall(block):
                font_name = match.strip()
                if font_name:
                    rec = touch(font_name)
                    if rec:
                        rec["inline_fn_occurrences"] += 1
                        rec["styles"].add(style_name or "<no-style>")
                        rec["roles"].add(style_role(style_name) if style_name else "inline_override")
                        rec["source_kinds"].add("inline_fn_override")
                    inline_override_events[font_name] += 1

            for match in RESET_TAG_RE.findall(block):
                reset_name = match.strip() or "Default"
                reset_style_counts[reset_name] += 1
                row = styles.get(reset_name)
                if row:
                    rec = touch(row.get("fontname", ""))
                    if rec:
                        rec["reset_style_events"] += 1
                        rec["styles"].add(reset_name)
                        rec["roles"].add(style_role(reset_name))
                        rec["source_kinds"].add("reset_style_override")

    for font_name in embedded_fonts:
        rec = touch(font_name)
        if rec:
            rec["embedded_font_entries"] += 1
            rec["source_kinds"].add("ass_embedded_font_section")

    unused_styles = sorted(
        name for name in styles
        if active_style_counts[name] == 0 and reset_style_counts[name] == 0
    )

    font_rows = []
    for name in sorted(font_stats, key=str.casefold):
        rec = font_stats[name]
        font_rows.append(
            {
                **rec,
                "styles": sorted(rec["styles"]),
                "roles": sorted(rec["roles"]),
                "source_kinds": sorted(rec["source_kinds"]),
            }
        )

    return {
        "source_file": source_name,
        "sha256": sha256,
        "script_info": script_info,
        "style_count": len(styles),
        "dialogue_event_count": len(dialogues),
        "comment_event_count": comment_event_count,
        "active_style_event_counts": dict(sorted(active_style_counts.items())),
        "reset_style_event_counts": dict(sorted(reset_style_counts.items())),
        "unused_style_names": unused_styles,
        "embedded_font_names_from_ass_fonts_section": embedded_fonts,
        "inline_font_override_event_counts": dict(sorted(inline_override_events.items())),
        "fonts": font_rows,
    }


def analyze_file(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text, encoding = decode_ass(raw)
    report = parse_ass_text(text, str(path), hashlib.sha256(raw).hexdigest())
    report["detected_encoding"] = encoding
    return report


def collect_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.casefold() not in {".ass", ".ssa"}:
            raise ValueError(f"Input file must end in .ass or .ssa: {input_path}")
        return [input_path]
    if not input_path.is_dir():
        raise FileNotFoundError(input_path)
    return sorted(
        (p for p in input_path.rglob("*") if p.is_file() and p.suffix.casefold() in {".ass", ".ssa"}),
        key=lambda p: str(p).casefold(),
    )


def write_reports(reports: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "ass_font_audit.json"
    csv_path = output_dir / "ass_font_audit.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"schema_version": "1.0", "files": reports}, f, ensure_ascii=False, indent=2)

    columns = [
        "source_file",
        "sha256",
        "font_name",
        "normalized_name_without_vertical_prefix",
        "style_definitions",
        "dialogue_style_events",
        "inline_fn_occurrences",
        "reset_style_events",
        "embedded_font_entries",
        "styles",
        "roles",
        "source_kinds",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for report in reports:
            for font in report["fonts"]:
                row = {key: font.get(key, "") for key in columns if key not in {"source_file", "sha256"}}
                row["source_file"] = report["source_file"]
                row["sha256"] = report["sha256"]
                for key in ("styles", "roles", "source_kinds"):
                    row[key] = "; ".join(font.get(key, []))
                writer.writerow(row)

    print(f"Analyzed {len(reports)} ASS/SSA file(s).")
    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract ASS/SSA font styles, active Dialogue usage and inline \\fn overrides."
    )
    parser.add_argument("--input", required=True, help="One .ass/.ssa file or a directory to scan recursively.")
    parser.add_argument("--output-dir", help="Output directory. Defaults to <input>/ass-font-audit-output.")
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    try:
        files = collect_inputs(input_path)
        if not files:
            print("No .ass or .ssa files found.", file=sys.stderr)
            return 2
        reports = []
        for path in files:
            try:
                reports.append(analyze_file(path))
            except Exception as exc:  # keep the other subtitle files in the batch
                reports.append({"source_file": str(path), "error": f"{type(exc).__name__}: {exc}"})
        if args.output_dir:
            output_dir = Path(args.output_dir).expanduser().resolve()
        elif input_path.is_dir():
            output_dir = input_path / "ass-font-audit-output"
        else:
            output_dir = input_path.parent / "ass-font-audit-output"
        write_reports(reports, output_dir)
        failed = sum("error" in r for r in reports)
        if failed:
            print(f"Warning: {failed} file(s) could not be parsed.", file=sys.stderr)
        return 1 if failed == len(reports) else 0
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
