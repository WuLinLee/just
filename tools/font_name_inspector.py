# -*- coding: utf-8 -*-
"""Portable Windows font metadata scanner using fontTools."""
from __future__ import annotations

import csv
import ctypes
import json
import os
import queue
import struct
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from fontTools import version as fonttools_version
from fontTools.ttLib import TTCollection, TTFont

APP_VERSION = "1.2.0"
SUPPORTED_EXTENSIONS = {".ttf", ".otf", ".ttc", ".otc"}
CSV_FIELDS = [
    "file", "relative_path", "extension", "file_size_bytes", "face_index",
    "sfnt_version", "family_name", "subfamily_name", "full_name",
    "postscript_name", "typographic_family_name", "typographic_subfamily_name",
    "wws_family_name", "wws_subfamily_name", "weight_class", "width_class",
    "bold", "italic", "variable_axes", "cmap_status", "cmap_error", "table_errors", "unicode_codepoints_count",
    "latin_basic_count", "latin1_count", "hiragana_count", "katakana_count",
    "cjk_basic_count", "cjk_ext_a_count", "cjk_ext_b_count",
    "hangul_syllable_count", "bopomofo_count", "all_name_records_json",
]
NAME_IDS = {
    "family_name": 1, "subfamily_name": 2, "full_name": 4, "postscript_name": 6,
    "typographic_family_name": 16, "typographic_subfamily_name": 17,
    "wws_family_name": 21, "wws_subfamily_name": 22,
}
LANGUAGE_PREFERENCE = {0x0409: 0, 0x0804: 1, 0x0404: 2, 0x0411: 3, 0x0412: 4}


def _record_text(record) -> str:
    try:
        return record.toUnicode()
    except Exception:
        try:
            return str(record.string, "utf-8", errors="replace")
        except Exception:
            return ""


def _get_name(name_table, name_id: int) -> str:
    if name_table is None:
        return ""
    try:
        value = name_table.getDebugName(name_id)
        if value:
            return str(value).strip()
    except Exception:
        pass
    candidates = []
    for record in getattr(name_table, "names", []):
        if getattr(record, "nameID", -1) != name_id:
            continue
        value = _record_text(record).strip()
        if not value:
            continue
        platform_id = getattr(record, "platformID", 9)
        language_id = getattr(record, "langID", -1)
        score = (
            0 if platform_id == 3 else 1 if platform_id == 0 else 2,
            LANGUAGE_PREFERENCE.get(language_id, 9),
            getattr(record, "encodingID", 99),
        )
        candidates.append((score, value))
    if candidates:
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]
    return ""


def _name_records(name_table) -> list[dict]:
    result = []
    if name_table is None:
        return result
    for record in getattr(name_table, "names", []):
        result.append({
            "name_id": getattr(record, "nameID", None),
            "platform_id": getattr(record, "platformID", None),
            "encoding_id": getattr(record, "platEncID", None),
            "language_id": getattr(record, "langID", None),
            "value": _record_text(record),
        })
    return result


def _count_range(codepoints: set[int], start: int, end: int) -> int:
    return sum(1 for cp in codepoints if start <= cp <= end)


def _parse_cmap4(sub_data: bytes, glyph_count: int | None) -> tuple[set[int], list[str]]:
    """Tolerantly parse a Unicode cmap format 4, skipping invalid glyph offsets."""
    if len(sub_data) < 16:
        raise ValueError("format 4 subtable is shorter than its header")
    declared_length = struct.unpack_from(">H", sub_data, 2)[0]
    if declared_length < 16 or declared_length > len(sub_data):
        raise ValueError(f"invalid format 4 length {declared_length}")
    data = sub_data[:declared_length]
    seg_count_x2 = struct.unpack_from(">H", data, 6)[0]
    if not seg_count_x2 or seg_count_x2 % 2:
        raise ValueError(f"invalid segCountX2 {seg_count_x2}")
    seg_count = seg_count_x2 // 2
    end_pos = 14
    start_pos = end_pos + 2 * seg_count + 2
    delta_pos = start_pos + 2 * seg_count
    range_pos = delta_pos + 2 * seg_count
    glyph_pos = range_pos + 2 * seg_count
    if glyph_pos > len(data):
        raise ValueError("format 4 segment arrays exceed subtable length")

    end_codes = struct.unpack_from(f">{seg_count}H", data, end_pos)
    start_codes = struct.unpack_from(f">{seg_count}H", data, start_pos)
    deltas = struct.unpack_from(f">{seg_count}H", data, delta_pos)
    range_offsets = struct.unpack_from(f">{seg_count}H", data, range_pos)
    glyph_array_bytes = data[glyph_pos:]
    glyph_array_count = len(glyph_array_bytes) // 2
    codepoints: set[int] = set()
    skipped = 0

    for i, (start_code, end_code, delta, range_offset) in enumerate(
        zip(start_codes, end_codes, deltas, range_offsets)
    ):
        if start_code > end_code:
            skipped += 1
            continue
        # U+FFFF is the required sentinel and is not a character mapping.
        upper = min(end_code, 0xFFFE)
        for codepoint in range(start_code, upper + 1):
            if range_offset == 0:
                glyph_id = (codepoint + delta) & 0xFFFF
            else:
                if range_offset % 2:
                    skipped += 1
                    continue
                index = codepoint + (range_offset // 2) - start_code + i - seg_count
                if not 0 <= index < glyph_array_count:
                    skipped += 1
                    continue
                glyph_id = struct.unpack_from(">H", glyph_array_bytes, index * 2)[0]
                if glyph_id:
                    glyph_id = (glyph_id + delta) & 0xFFFF
            if glyph_id and (glyph_count is None or glyph_id < glyph_count):
                codepoints.add(codepoint)

    warnings = []
    if skipped:
        warnings.append(f"format 4 skipped {skipped} invalid segment/codepoint entries")
    return codepoints, warnings


def _parse_cmap12_or_13(
    sub_data: bytes, fmt: int, glyph_count: int | None
) -> tuple[set[int], list[str]]:
    """Parse format 12/13, tolerating harmless trailing padding and truncation."""
    if len(sub_data) < 16:
        raise ValueError(f"format {fmt} subtable is shorter than its header")
    declared_length = struct.unpack_from(">I", sub_data, 4)[0]
    group_count = struct.unpack_from(">I", sub_data, 12)[0]
    expected_length = 16 + group_count * 12
    if declared_length < 16 or declared_length > len(sub_data):
        raise ValueError(
            f"format {fmt} invalid declared length {declared_length}, available {len(sub_data)}"
        )
    available_length = min(declared_length, len(sub_data))
    complete_groups = max(0, (available_length - 16) // 12)
    parse_groups = min(group_count, complete_groups)
    if not parse_groups:
        raise ValueError(f"format {fmt} has no complete mapping groups")

    codepoints: set[int] = set()
    warnings = []
    if declared_length > expected_length:
        warnings.append(
            f"format {fmt} ignored {declared_length - expected_length} trailing padding bytes"
        )
    if declared_length < expected_length or parse_groups < group_count:
        warnings.append(
            f"format {fmt} recovered {parse_groups} of {group_count} mapping groups"
        )

    last_end = -1
    for i in range(parse_groups):
        start, end, start_glyph = struct.unpack_from(">LLL", sub_data, 16 + i * 12)
        end = min(end, 0x10FFFF)
        if start > end or start <= last_end:
            warnings.append(f"format {fmt} skipped invalid/overlapping group {i}")
            continue
        last_end = end

        if fmt == 13:
            if start_glyph == 0 or (glyph_count is not None and start_glyph >= glyph_count):
                continue
            codepoints.update(range(start, end + 1))
            continue

        # Format 12 increments the glyph ID with the codepoint.
        first_valid_cp = start
        if start_glyph == 0:
            first_valid_cp += 1
        if glyph_count is not None:
            if start_glyph >= glyph_count:
                continue
            end = min(end, start + (glyph_count - 1 - start_glyph))
        if first_valid_cp <= end:
            codepoints.update(range(first_valid_cp, end + 1))

    return codepoints, warnings


def _parse_simple_cmap(sub_data: bytes, fmt: int, glyph_count: int | None) -> tuple[set[int], list[str]]:
    """Parse the compact Unicode cmap formats 0 and 6."""
    if fmt == 0:
        if len(sub_data) < 262:
            raise ValueError("format 0 subtable is truncated")
        gids = sub_data[6:262]
        return {
            cp for cp, gid in enumerate(gids)
            if gid and (glyph_count is None or gid < glyph_count)
        }, []
    if fmt == 6:
        if len(sub_data) < 10:
            raise ValueError("format 6 subtable is shorter than its header")
        first_code, entry_count = struct.unpack_from(">HH", sub_data, 6)
        available = max(0, (len(sub_data) - 10) // 2)
        count = min(entry_count, available)
        gids = struct.unpack_from(f">{count}H", sub_data, 10) if count else ()
        warnings = [] if count == entry_count else [
            f"format 6 recovered {count} of {entry_count} glyph entries"
        ]
        return {
            first_code + i for i, gid in enumerate(gids)
            if gid and (glyph_count is None or gid < glyph_count)
        }, warnings
    raise ValueError(f"unsupported cmap format {fmt}")


def _get_unicode_codepoints(font) -> tuple[set[int] | None, str, str]:
    """Read Unicode cmap subtables independently so one broken subtable cannot hide others."""
    try:
        raw = font.reader["cmap"] if font.reader is not None else b""
    except Exception as exc:
        return None, "parse_error", f"cannot read cmap bytes: {type(exc).__name__}: {exc}"
    if len(raw) < 4:
        return None, "parse_error", "cmap table is missing or truncated"

    try:
        version, count = struct.unpack_from(">HH", raw, 0)
        if version != 0:
            return None, "parse_error", f"unsupported cmap table version {version}"
        if 4 + count * 8 > len(raw):
            return None, "parse_error", "cmap encoding-record directory is truncated"
    except Exception as exc:
        return None, "parse_error", f"invalid cmap header: {type(exc).__name__}: {exc}"

    try:
        glyph_count = int(font["maxp"].numGlyphs) if "maxp" in font else None
    except Exception:
        glyph_count = None

    preference = {
        (3, 10): 0, (0, 6): 1, (0, 4): 2, (3, 1): 3,
        (0, 3): 4, (0, 2): 5, (0, 1): 6, (0, 0): 7,
    }
    entries = []
    for i in range(count):
        platform, encoding, offset = struct.unpack_from(">HHL", raw, 4 + i * 8)
        if not (platform == 0 or (platform == 3 and encoding in (0, 1, 10))):
            continue
        if offset + 2 > len(raw):
            continue
        fmt = struct.unpack_from(">H", raw, offset)[0]
        entries.append((preference.get((platform, encoding), 8), offset, fmt))

    if not entries:
        return None, "no_unicode_cmap", "no Unicode cmap subtables were found"

    entries.sort(key=lambda item: item[0])
    seen_offsets = set()
    candidates = []
    diagnostics = []

    for rank, offset, fmt in entries:
        if offset in seen_offsets:
            continue
        seen_offsets.add(offset)
        try:
            if fmt in (8, 10, 12, 13):
                if offset + 8 > len(raw):
                    raise ValueError("extended cmap header is truncated")
                length = struct.unpack_from(">I", raw, offset + 4)[0]
            elif fmt == 14:
                continue  # Unicode variation selector table, not a base cmap.
            else:
                if offset + 4 > len(raw):
                    raise ValueError("cmap subtable header is truncated")
                length = struct.unpack_from(">H", raw, offset + 2)[0]
            if length < 4 or offset + length > len(raw):
                raise ValueError(
                    f"invalid subtable bounds: offset={offset}, length={length}, cmap_size={len(raw)}"
                )
            sub_data = raw[offset:offset + length]

            if fmt == 4:
                codepoints, warnings = _parse_cmap4(sub_data, glyph_count)
            elif fmt in (12, 13):
                codepoints, warnings = _parse_cmap12_or_13(sub_data, fmt, glyph_count)
            elif fmt in (0, 6):
                codepoints, warnings = _parse_simple_cmap(sub_data, fmt, glyph_count)
            else:
                raise ValueError(f"unsupported Unicode cmap format {fmt}")

            if warnings:
                diagnostics.extend([f"format {fmt} @ {offset}: {item}" for item in warnings])
            if codepoints:
                candidates.append((rank, codepoints, fmt))
        except Exception as exc:
            diagnostics.append(
                f"format {fmt} @ {offset}: {type(exc).__name__}: {exc}"
            )

    if not candidates:
        detail = "; ".join(diagnostics) if diagnostics else "no usable Unicode cmap subtable"
        return None, "parse_error", detail

    # Choose the fullest successfully decoded Unicode map. Break ties by
    # OpenType/libass-like platform preference ordering.
    candidates.sort(key=lambda item: (-len(item[1]), item[0]))
    chosen_rank, chosen, chosen_format = candidates[0]
    status = "recovered" if diagnostics else "ok"
    detail = "; ".join(diagnostics)
    if not detail:
        detail = f"decoded Unicode cmap format {chosen_format}"
    else:
        detail = f"selected format {chosen_format}; " + detail
    return chosen, status, detail


def _inspect_face(font, path: Path, root: Path, face_index: int | str) -> dict:
    table_errors = []

    # The name table is read independently. A malformed cmap must not erase
    # the internal family / subfamily / PostScript names.
    try:
        name_table = font["name"] if "name" in font else None
    except Exception as exc:
        name_table = None
        table_errors.append(f"name: {type(exc).__name__}: {exc}")
    names = {field: _get_name(name_table, name_id) for field, name_id in NAME_IDS.items()}
    try:
        name_records = _name_records(name_table)
    except Exception as exc:
        name_records = []
        table_errors.append(f"name records: {type(exc).__name__}: {exc}")

    try:
        os2 = font["OS/2"] if "OS/2" in font else None
    except Exception as exc:
        os2 = None
        table_errors.append(f"OS/2: {type(exc).__name__}: {exc}")
    try:
        head = font["head"] if "head" in font else None
    except Exception as exc:
        head = None
        table_errors.append(f"head: {type(exc).__name__}: {exc}")

    weight_class = getattr(os2, "usWeightClass", "") if os2 else ""
    width_class = getattr(os2, "usWidthClass", "") if os2 else ""
    fs_selection = getattr(os2, "fsSelection", 0) if os2 else 0
    mac_style = getattr(head, "macStyle", 0) if head else 0
    is_bold = bool((fs_selection & (1 << 5)) or (mac_style & 1) or (weight_class and weight_class >= 700))
    is_italic = bool((fs_selection & 1) or (mac_style & 2))

    # A number of older font collections contain malformed cmap subtables.
    # Keep the metadata row; report coverage as unavailable instead of zero.
    coverage = {
        "unicode_codepoints_count": "",
        "latin_basic_count": "",
        "latin1_count": "",
        "hiragana_count": "",
        "katakana_count": "",
        "cjk_basic_count": "",
        "cjk_ext_a_count": "",
        "cjk_ext_b_count": "",
        "hangul_syllable_count": "",
        "bopomofo_count": "",
    }
    cmap_status = "unavailable"
    cmap_error = ""
    codepoints, cmap_status, cmap_error = _get_unicode_codepoints(font)
    if codepoints is None:
        if cmap_status == "no_unicode_cmap":
            coverage = {key: 0 for key in coverage}
    else:
        coverage = {
            "unicode_codepoints_count": len(codepoints),
            "latin_basic_count": _count_range(codepoints, 0x0020, 0x007E),
            "latin1_count": _count_range(codepoints, 0x00A0, 0x00FF),
            "hiragana_count": _count_range(codepoints, 0x3040, 0x309F),
            "katakana_count": _count_range(codepoints, 0x30A0, 0x30FF),
            "cjk_basic_count": _count_range(codepoints, 0x4E00, 0x9FFF),
            "cjk_ext_a_count": _count_range(codepoints, 0x3400, 0x4DBF),
            "cjk_ext_b_count": _count_range(codepoints, 0x20000, 0x2A6DF),
            "hangul_syllable_count": _count_range(codepoints, 0xAC00, 0xD7AF),
            "bopomofo_count": _count_range(codepoints, 0x3100, 0x312F),
        }

    axes = []
    try:
        if "fvar" in font:
            for axis in font["fvar"].axes:
                axes.append({
                    "tag": getattr(axis, "axisTag", ""),
                    "min": getattr(axis, "minValue", None),
                    "default": getattr(axis, "defaultValue", None),
                    "max": getattr(axis, "maxValue", None),
                })
    except Exception as exc:
        table_errors.append(f"fvar: {type(exc).__name__}: {exc}")

    try:
        relative_path = str(path.relative_to(root))
    except Exception:
        relative_path = str(path)

    return {
        "file": path.name, "relative_path": relative_path,
        "extension": path.suffix.lower(), "file_size_bytes": path.stat().st_size,
        "face_index": face_index, "sfnt_version": str(getattr(font, "sfntVersion", "")),
        **names,
        "weight_class": weight_class, "width_class": width_class,
        "bold": is_bold, "italic": is_italic,
        "variable_axes": json.dumps(axes, ensure_ascii=False, separators=(",", ":")),
        "cmap_status": cmap_status,
        "cmap_error": cmap_error,
        **coverage,
        "table_errors": " | ".join(table_errors),
        "all_name_records_json": json.dumps(
            name_records, ensure_ascii=False, separators=(",", ":")
        ),
    }

def _inspect_file(path: Path, root: Path) -> list[dict]:
    # Inspect the file signature, not its extension. A few old font collections
    # in user libraries are TTC containers renamed with a .TTF suffix.
    with path.open("rb") as handle:
        signature = handle.read(4)

    rows = []
    if signature == b"ttcf":
        collection = TTCollection(
            str(path), lazy=True, ignoreDecompileErrors=True
        )
        try:
            # TTC faces share one underlying file handle. Keep the collection
            # open until every face has been inspected.
            for index, font in enumerate(collection.fonts):
                rows.append(_inspect_face(font, path, root, index))
        finally:
            collection.close()
    else:
        font = TTFont(
            str(path), lazy=True, ignoreDecompileErrors=True
        )
        try:
            rows.append(_inspect_face(font, path, root, ""))
        finally:
            font.close()
    return rows

def _find_fonts(root: Path, recursive: bool) -> list[Path]:
    found = []
    if recursive:
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs.sort(key=str.casefold)
            for filename in files:
                path = Path(current) / filename
                if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    found.append(path)
    else:
        for path in root.iterdir():
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                found.append(path)
    found.sort(key=lambda item: str(item).casefold())
    return found


def _get_desktop_directory() -> Path:
    """Return the actual Windows Desktop known folder, including OneDrive redirects."""
    if os.name == "nt":
        # Windows Known Folder API respects moved / OneDrive-synced desktops.
        try:
            from ctypes import wintypes

            class GUID(ctypes.Structure):
                _fields_ = [
                    ("Data1", ctypes.c_ulong),
                    ("Data2", ctypes.c_ushort),
                    ("Data3", ctypes.c_ushort),
                    ("Data4", ctypes.c_ubyte * 8),
                ]

            desktop_id = GUID(
                0xB4BFCC3A, 0xDB2C, 0x424C,
                (ctypes.c_ubyte * 8)(0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41),
            )
            shell32 = ctypes.WinDLL("shell32", use_last_error=True)
            ole32 = ctypes.WinDLL("ole32")
            get_folder = shell32.SHGetKnownFolderPath
            get_folder.argtypes = [
                ctypes.POINTER(GUID), wintypes.DWORD, wintypes.HANDLE,
                ctypes.POINTER(wintypes.LPWSTR),
            ]
            get_folder.restype = ctypes.c_long
            path_buffer = wintypes.LPWSTR()
            result = get_folder(ctypes.byref(desktop_id), 0, None, ctypes.byref(path_buffer))
            if result == 0 and path_buffer.value:
                desktop = Path(path_buffer.value)
                ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
                ole32.CoTaskMemFree(ctypes.cast(path_buffer, ctypes.c_void_p))
                if desktop.exists():
                    return desktop
        except Exception:
            pass

        # Fallback: the Shell User Shell Folders registry value also supports
        # redirected and OneDrive desktops.
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "Desktop")
            desktop = Path(os.path.expandvars(value)).expanduser()
            if desktop.exists():
                return desktop
        except Exception:
            pass

    return Path.home() / "Desktop"


def _write_reports(root: Path, records: list[dict], errors: list[dict]) -> dict:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Keep all output files together in a dedicated folder on the real Desktop.
    output_dir = _get_desktop_directory() / "FontNameInspector_扫描结果"
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"font_inventory_{stamp}.csv"
    json_path = output_dir / f"font_inventory_{stamp}.json"
    errors_path = output_dir / f"font_scan_errors_{stamp}.txt" if errors else None

    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    payload = {
        "application": "Font Name Inspector",
        "application_version": APP_VERSION,
        "fonttools_version": fonttools_version,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scanned_directory": str(root),
        "output_directory": str(output_dir),
        "font_file_count": len({row["relative_path"] for row in records}),
        "font_face_count": len(records),
        "error_count": len(errors),
        "records": records,
        "errors": errors,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if errors_path:
        lines = [f'{item["file"]}\n  {item["error"]}\n' for item in errors]
        errors_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "csv": str(csv_path), "json": str(json_path),
        "errors": str(errors_path) if errors_path else "",
        "output_dir": str(output_dir),
    }

class FontInspectorApp:
    def __init__(self, window: tk.Tk):
        self.root = window
        self.root.title("Font Name Inspector - 字体真实名称扫描器")
        self.root.geometry("900x650")
        self.root.minsize(760, 540)
        self.events: queue.Queue = queue.Queue()
        self.last_reports = None
        self.scanning = False
        initial_path = ""
        if len(sys.argv) > 1:
            candidate = Path(sys.argv[1].strip('"'))
            if candidate.exists() and candidate.is_dir():
                initial_path = str(candidate)
        self.path_var = tk.StringVar(value=initial_path)
        self.recursive_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="选择字体文件夹，然后点击“开始扫描”。")
        self._build_ui()
        self.root.after(100, self._process_events)

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="字体真实名称扫描器", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="读取 TTF / OTF / TTC / OTC 的内部字体名称、字重和 Unicode 字符覆盖；不依赖文件名。",
            wraplength=850,
        ).pack(anchor="w", pady=(4, 14))

        path_row = ttk.Frame(outer)
        path_row.pack(fill="x")
        ttk.Label(path_row, text="字体目录：").pack(side="left")
        self.path_entry = ttk.Entry(path_row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(4, 8))
        self.browse_button = ttk.Button(path_row, text="浏览…", command=self._browse)
        self.browse_button.pack(side="left")

        options = ttk.Frame(outer)
        options.pack(fill="x", pady=(8, 10))
        self.recursive_check = ttk.Checkbutton(options, text="扫描所有子文件夹（推荐）", variable=self.recursive_var)
        self.recursive_check.pack(side="left")
        self.start_button = ttk.Button(options, text="开始扫描", command=self._start_scan)
        self.start_button.pack(side="right")

        self.progress = ttk.Progressbar(outer, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(4, 6))
        ttk.Label(outer, textvariable=self.status_var).pack(anchor="w", pady=(0, 8))

        log_frame = ttk.LabelFrame(outer, text="扫描日志", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, height=18, wrap="word", state="disabled", font=("Consolas", 9))
        scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        bottom = ttk.Frame(outer)
        bottom.pack(fill="x", pady=(12, 0))
        self.open_folder_button = ttk.Button(bottom, text="打开结果文件夹", command=self._open_output, state="disabled")
        self.open_folder_button.pack(side="left")
        self.open_csv_button = ttk.Button(bottom, text="打开 CSV", command=self._open_csv, state="disabled")
        self.open_csv_button.pack(side="left", padx=(8, 0))
        ttk.Label(bottom, text=f"v{APP_VERSION}  |  FontTools {fonttools_version}").pack(side="right")
        self._log("提示：也可以把字体文件夹直接拖到 FontNameInspector.exe 图标上。")
        self._log("扫描结果统一保存在桌面上的 FontNameInspector_扫描结果 文件夹中。")

    def _log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _browse(self):
        selected = filedialog.askdirectory(title="选择要扫描的字体文件夹")
        if selected:
            self.path_var.set(selected)

    def _start_scan(self):
        if self.scanning:
            return
        raw_path = self.path_var.get().strip().strip('"')
        if not raw_path:
            messagebox.showwarning("还没有选择目录", "请先选择你的字体文件夹。")
            return
        root = Path(raw_path).expanduser()
        if not root.exists() or not root.is_dir():
            messagebox.showerror("目录无效", f"找不到这个文件夹：\n{root}")
            return
        self.scanning = True
        self.last_reports = None
        self.progress.configure(value=0, maximum=100)
        self.status_var.set("正在准备扫描…")
        self.start_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.open_folder_button.configure(state="disabled")
        self.open_csv_button.configure(state="disabled")
        self._log(f"\n开始扫描：{root}")
        threading.Thread(target=self._scan_worker, args=(root, self.recursive_var.get()), daemon=True).start()

    def _scan_worker(self, root: Path, recursive: bool):
        records, errors = [], []
        try:
            files = _find_fonts(root, recursive)
            self.events.put(("log", f"找到 {len(files)} 个字体文件，正在读取内部字体信息…"))
            self.events.put(("progress", 0, max(len(files), 1)))
            for index, path in enumerate(files, start=1):
                try:
                    face_rows = _inspect_file(path, root)
                    records.extend(face_rows)
                    # Also include face-level table issues in the TXT report.
                    # A bad cmap does not discard the face's recovered metadata.
                    for row in face_rows:
                        face_issues = []
                        if row.get("cmap_status") in ("parse_error", "recovered"):
                            face_issues.append(
                                "cmap " + row.get("cmap_status") + ": "
                                + row.get("cmap_error", "存在非标准或无法解析的子表")
                            )
                        if row.get("table_errors"):
                            face_issues.append(row["table_errors"])
                        if face_issues:
                            errors.append({
                                "file": f"{path} [face {row.get('face_index', '')}]",
                                "error": " | ".join(face_issues),
                            })
                    self.events.put(("log", f"[{index}/{len(files)}] {path.name}：读取 {len(face_rows)} 个字体面"))
                except Exception as exc:
                    errors.append({"file": str(path), "error": f"{type(exc).__name__}: {exc}"})
                    self.events.put(("log", f"[跳过] {path.name}：{type(exc).__name__}: {exc}"))
                self.events.put(("progress", index, max(len(files), 1)))
            reports = _write_reports(root, records, errors)
            self.events.put(("done", reports, len(files), len(records), len(errors)))
        except Exception as exc:
            self.events.put(("fatal", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"))

    def _process_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "log":
                    self._log(event[1])
                elif kind == "progress":
                    current, total = event[1], event[2]
                    self.progress.configure(maximum=total, value=current)
                    self.status_var.set(f"正在扫描：{current} / {total}")
                elif kind == "done":
                    reports, file_count, face_count, error_count = event[1:]
                    self.last_reports = reports
                    self.scanning = False
                    self.start_button.configure(state="normal")
                    self.browse_button.configure(state="normal")
                    self.open_folder_button.configure(state="normal")
                    self.open_csv_button.configure(state="normal")
                    self.status_var.set(f"完成：{file_count} 个文件，{face_count} 个字体面，{error_count} 个解析问题/警告。")
                    self._log("\n扫描完成！")
                    self._log(f"CSV：{reports['csv']}")
                    self._log(f"JSON：{reports['json']}")
                    if reports["errors"]:
                        self._log(f"错误日志：{reports['errors']}")
                    self._log("把 CSV 上传给 ChatGPT，就可以继续核对 ASS 字幕的字体请求。")
                    messagebox.showinfo(
                        "扫描完成",
                        f"字体文件：{file_count}\n字体面：{face_count}\n读取错误：{error_count}\n\nCSV 已生成：\n{reports['csv']}",
                    )
                elif kind == "fatal":
                    self.scanning = False
                    self.start_button.configure(state="normal")
                    self.browse_button.configure(state="normal")
                    self.status_var.set("扫描失败。")
                    self._log("扫描失败：" + event[1])
                    messagebox.showerror("扫描失败", event[1])
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)

    def _open_output(self):
        if self.last_reports:
            os.startfile(self.last_reports["output_dir"])

    def _open_csv(self):
        if self.last_reports:
            os.startfile(self.last_reports["csv"])


def main():
    window = tk.Tk()
    FontInspectorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
