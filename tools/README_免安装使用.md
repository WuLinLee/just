# Font Name Inspector（Windows 免安装版）

## 下载和使用

1. 打开本仓库的 [Releases 页面](https://github.com/WuLinLee/just/releases/latest)。
2. 下载 FontNameInspector-Portable.zip 并解压。
3. 双击 FontNameInspector.exe。
4. 点击“浏览…”选择字体目录，例如 E:\mpv-lazy\font for mpv。
5. 点击“开始扫描”。也可以把字体目录直接拖到 exe 图标上启动。

**本机不需要安装 Python、pip 或 FontTools，也不需要联网。** 程序由 GitHub Actions 在 Windows 云端构建为独立可执行文件。

## 输出结果

三个结果文件集中保存在 Windows 实际桌面（自动识别移动桌面／OneDrive 桌面）下的文件夹：

`桌面\\FontNameInspector_扫描结果\\`

文件名带扫描时间戳，避免覆盖上一次结果：

- font_inventory_时间戳.csv：Excel 可打开，使用 UTF-8 BOM 编码。
- font_inventory_时间戳.json：完整结构化数据。
- font_scan_errors_时间戳.txt：仅在有无法读取的字体时生成。

如果目标目录没有写入权限，结果会保存到“文档\FontNameInspector”。

## 扫描内容

- TTF / OTF / TTC / OTC 字体文件；会检查文件头，因此扩展名为 .TTF 的实际 TTC 集合也能识别。
- 对旧式字体的非标准 cmap 表采用容错读取：逐个解析 Unicode cmap 子表，跳过损坏的 format 4 段；对 format 12/13 忽略超出组数据的尾随填充字节。尽量恢复字符覆盖；仍无法恢复时，在 CSV 标注 cmap_status / cmap_error，而不是将覆盖数误写为 0。
- cmap_status 为 ok 表示正常解析，recovered 表示跳过／修复非标准子表后恢复了字符覆盖，parse_error 表示仍无法解析。
- 每个 TTC / OTC 内的每一个字体面（face index）。
- Family、Subfamily、Full Name、PostScript Name。
- Typographic Family / Subfamily、WWS Family / Subfamily。
- OS/2 Weight Class、Width Class、Bold / Italic 标记。
- Unicode cmap 字符数，以及拉丁、平假名、片假名、中日韩统一表意文字、韩文、注音符号覆盖数量。
- 所有 name table 记录（包含平台和语言编号）。

## 注意事项

- 扫描字体文件内部元数据，不是仅根据文件名猜测。
- 不会模拟 Windows DirectWrite 或 libass 的完整字体匹配算法；最终仍应使用 mpv 播放真实 ASS 样本验证。
- 默认递归扫描普通子目录，不跟随目录符号链接，以避免循环扫描。
- 输出文件：CSV（Excel 字体清单）、JSON（完整元数据）、TXT（存在读取错误时生成的错误记录）。
- 只读取字体，不会安装、修改或删除字体文件。

## 构建方式

由 .github/workflows/build-font-inspector.yml 使用 GitHub Actions 在 Windows runner 上构建。
构建依赖版本见 tools/requirements-build.txt。
