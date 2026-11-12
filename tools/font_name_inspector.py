# -*- coding: utf-8 -*-
"""Portable Windows font metadata scanner using fontTools."""
from __future__ import annotations

import csv
import json
import os
import queue
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from fontTools import version as fonttools_version
from fontTools.ttLib import TTCollection, TTFont

APP_VERSION = "1.0.0"
SUPPORTED_EXTENSIONS = {".ttf", ".otf", ".ttc", ".otc"}
CSV_FIELDS = [
    "file", "relative_path", "extension", "file_size_bytes", "face_index",
    "sfnt_version", "family_name", "subfamily_name", "full_name",
    "postscript_name", "typographic_family_name", "typographic_subfamily_name",
    "wws_family_name", "wws_subfamily_name", "weight_class", "width_class",
    "bold", "italic", "variable_axes", "unicode_codepoints_count",
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


def _inspect_face(font, path: Path, root: Path, face_index: int | str) -> dict:
    name_table = font["name"] if "name" in font else None
    names = {field: _get_name(name_table, name_id) for field, name_id in NAME_IDS.items()}
    os2 = font["OS/2"] if "OS/2" in font else None
    head = font["head"] if "head" in font else None
    weight_class = getattr(os2, "usWeightClass", "") if os2 else ""
    width_class = getattr(os2, "usWidthClass", "") if os2 else ""
    fs_selection = getattr(os2, "fsSelection", 0) if os2 else 0
    mac_style = getattr(head, "macStyle", 0) if head else 0
    is_bold = bool((fs_selection & (1 << 5)) or (mac_style & 1) or (weight_class and weight_class >= 700))
    is_italic = bool((fs_selection & 1) or (mac_style & 2))
    codepoints = set((font.getBestCmap() or {}).keys())
    axes = []
    if "fvar" in font:
        for axis in font["fvar"].axes:
            axes.append({
                "tag": getattr(axis, "axisTag", ""),
                "min": getattr(axis, "minValue", None),
                "default": getattr(axis, "defaultValue", None),
                "max": getattr(axis, "maxValue", None),
            })
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
        "all_name_records_json": json.dumps(
            _name_records(name_table), ensure_ascii=False, separators=(",", ":")
        ),
    }


def _inspect_file(path: Path, root: Path) -> list[dict]:
    rows = []
    if path.suffix.lower() in {".ttc", ".otc"}:
        collection = TTCollection(str(path), lazy=True)
        try:
            # TTCollection fonts share one underlying file handle. Do not close
            # each face inside the loop; close the collection after all faces
            # have been inspected.
            for index, font in enumerate(collection.fonts):
                rows.append(_inspect_face(font, path, root, index))
        finally:
            collection.close()
    else:
        font = TTFont(str(path), lazy=True)
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


def _write_reports(root: Path, records: list[dict], errors: list[dict]) -> dict:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = root
    try:
        test_path = output_dir / f".font_inspector_write_test_{stamp}.tmp"
        test_path.write_text("ok", encoding="utf-8")
        test_path.unlink(missing_ok=True)
    except Exception:
        output_dir = Path.home() / "Documents" / "FontNameInspector"
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
        self._log("扫描结果默认保存在被扫描的字体目录中。")

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
                    self.status_var.set(f"完成：{file_count} 个文件，{face_count} 个字体面，{error_count} 个错误。")
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
