# Handoff：mpv 字体库存 × 字幕组 ASS 审计

> 更新：2026-11-16。接手前先读仓库根目录的 `README.md`、`FONT_GAP_LIST.md` 和 `FONT_INVENTORY_AUDIT.md`。

## 用户目标

用户维护 Windows/mpv 的动漫、日剧、电影外挂 ASS 字幕字体库，希望依据真实字幕组 ASS 的主对白、注释、歌词、标题、屏幕字及特效字体，整理 Core 与 Optional 精选包，并持续扩展字幕组样本。

## 分支用途

- `main`：字体扫描工具、原始全量库存、人工缺口清单、全量扫描报告。
- `new`：同样的库存/缺口资料，加上本目录的字幕组 ASS 字体研究、样本与解析脚本。
- 用户已明确授权本轮对 main 和 new 两个分支更新。
- 不要上传商业字体二进制或未经授权的字幕文件。

## 最新的原始字体库基准

根目录三份原始输出：
- `font_inventory_20261112_151422.csv`
- `font_inventory_20261112_151422.json`
- `font_scan_errors_20261112_151422.txt`

来自 `E:\mpv-lazy\font for mpv`，扫描时间 2026-11-12 15:14:22 +08:00，Font Name Inspector 1.2.0 / FontTools 4.68.0：
- 1,061 个字体文件；
- 1,695 个字体 face；
- 1,435 个 cmap 正常；
- 203 个 cmap recovered（涉及 75 个文件），是容错恢复日志，不是 203 个坏文件；
- 57 个 face（45 个文件）没有 Unicode cmap；
- 所有 face 的 name/OS2/head 等表读取错误为 0。

旧 README 和旧缺口表写过 2026-11-10 的 613 项目录树；这是较早且不同口径的文件列表，不能当成 2026-11-12 扫描的记录数。

## 40 个 ASS 候选与原始库存对照

对候选 ASS 名称、别名，及 Family/Subfamily/Full Name/PostScript/Typographic/WWS 与所有 name table 记录进行精确对照：
- 31 项精确存在；
- 8 项未检出；
- Arial 1 项不在该文件夹，需先查 Windows 系统字体。

详细文件名、face index、内部名称、OS/2 Weight Class 和 cmap 状态：
- `data/ass-font-inventory-comparison.csv`
- 同步总表：`../../inventory/ass-font-inventory-comparison.csv`

精确未检出的 8 项：
1. 森泽UD新黑 Gb4 R（同族 M 已有）
2. 方正胖娃_GBK
3. FOT-CookHand Std R
4. FOT-UDMarugo_Large Pr6N E（同族 B 已有）
5. A-OTF Kocho Std Heavy
6. Kozuka Mincho Pr6N M（其他 Kozuka Mincho 系列/字重在目录）
7. Kozuka Gothic Pro R（其他系列/字重在目录）
8. FA 隷書Ｍ

不要重复下载：Dream Han Sans SC/J W20、Dream Han Serif SC/J W14、华康圆体W7-A、华康方圆体W7(P)、华康翩翩体W5-A/W3-A、森泽UD新黑 Gb4 M、A-OTF UD Shin Go Pr6N M、汉仪正圆75/85S、汉仪玄宋75S、思源黑体SC/TC Medium、思源宋体SC/TC SemiBold 等，见 31 个 PRESENT 项。

## 51 文件 Core/Optional 精选包仍未完成差集

之前用户 PowerShell 报告：
- Core 41 个文件；
- Optional 10 个文件；
- 共 51 个；
- Core 396.3 MB、Optional 266.2 MB，总计 662.5 MB。

但最终 `manifest.csv` 尚未收到。因此 31/8 结果只针对原始 1,061 文件目录，不可推断 51 精选包内的存在/缺失。后续拿到 manifest 后，需分别核对 Core 与 Optional 的文件名、内部名称、字重、TTC face 与 cmap。

## cmap 质量提示

- 203 条 recovered cmap 记录并非不可读取字体；详见 `../../inventory/recovered-cmap-faces.csv`。
- 57 条 no-Unicode-cmap face 即使内部名字可读取，也可能依赖旧编码；详见 `../../inventory/no-unicode-cmap-faces.csv`。
- 不模拟 Windows DirectWrite 或 mpv/libass，必须真实播放检查 fallback、地区字形和缺字。

## ASS 样本与归属

研究覆盖 Nekomoe kissaten、SweetSub、MingYSub、KitaujiSub、轻之国度、千夏/Airota、UHA-WINGS、LoliHouse、KTXP/VCB、SumiSora 等。重要规则：
- ASS 注释/Original Script/制作署名优先于压制文件名前缀。
- VCB-Studio 常是压制/发布标记，不能直接当作字幕制作组。
- 不把一个 ASS 内全部 Style 字体都算成主对白字体；需要看实际 Dialogue 使用、行内 `\fn`、重置 `\r`、注释事件和内嵌字体。
- OP/ED、标题、Staff、屏幕字与正片对白分开分类。

## 仓库工具文件已检查

- `tools/font_name_inspector.py`：读取字体内部名称、TTC face、字重、cmap 和所有 name records。
- `tools/README_免安装使用.md`：工具输出与状态解释。
- `tools/tests/test_cmap_recovery.py`：cmap format4/12/13 容错测试。
- `.github/workflows/build-font-inspector.yml`：Windows 云端构建与测试/release。
- `research/.../scripts/ass_font_audit.py`：标准库 ASS/SSA 静态提取。
- `research/.../tests/test_ass_font_audit.py`：ASS 解析最小测试。

注意：本轮未实际运行 Python 单测，也未在用户 mpv 中播放，不能宣称测试通过。

## 下一步优先级

1. 让用户提供 51 文件包现有 `manifest.csv`，做 Core/Optional 精确差集。
2. 对 57 个 no-Unicode cmap face，检查 legacy encoding、Unicode 映射与实机 mpv/libass 表现。
3. 对 203 个 recovered cmap 面抽查重要 CJK 字符覆盖，尤其注意损坏段跳过是否导致缺字。
4. 扩充同一字幕组跨作品 ASS，优先主对白证据，不只收歌词/标题。
5. 真实播放验证时记录 mpv/libass 版本、`sub-fonts-dir`、字幕来源、字体加载日志和截图。

## 文件导航

- `data/ass-samples.csv`：34 个公开 ASS 样本与来源
- `data/font-candidates.csv`：40 项 ASS 候选及 1,061 库存状态
- `data/ass-font-inventory-comparison.csv`：逐条文件/face/内部名称比对
- `data/group-font-evidence.json`：字幕组/作品结构化观察
- `docs/ass-font-audit-method.md`：ASS 分析判断方法
- `scripts/ass_font_audit.py`：ASS/SSA 批量静态提取器
- `tests/test_ass_font_audit.py`：最小解析测试
