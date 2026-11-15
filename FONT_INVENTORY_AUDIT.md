# Font for mpv 全量库存扫描审计

> 扫描时间：2026-11-12T15:14:22+08:00（扫描机器时区）
> 来源目录：`E:\mpv-lazy\font for mpv`
> 工具：Font Name Inspector 1.2.0 / FontTools 4.68.0
> 对照依据：字体内部 Family、Subfamily、Full Name、PostScript、Typographic/WWS 及所有 name table 记录。

## 一、库存统计

| 指标 | 数值 |
|---|---:|
| 字体文件 | **1,061** |
| 字体 face（TTC/OTC 每个 face 分开计数） | **1,695** |
| cmap 正常解析 | 1435 |
| cmap 容错恢复 | 203 |
| 无 Unicode cmap 子表 | 57 |
| name/OS2/head 等表读取错误 | 0 |
| 日志中的解析问题／警告条目 | 203 |

CSV 每一行代表一个字体 face，而不是一个文件。一个 TTC 可包含多个地区/语言 face；只看文件名和文件数会漏掉实际已包含的字体名称。

## 二、203 条日志的正确含义

本次 203 条日志全部对应 `cmap_status=recovered` 的字体 face，涉及 75 个文件。扫描器尝试从非标准 cmap 子表恢复 Unicode 映射，记录了跳过损坏段或尾随填充的诊断信息。它们不是 203 个无法读取的字体：这 203 条都保留了内部名称和恢复后的 cmap 数据。

因此：
- `error_count=203` 是工具的“解析问题／警告”记录数，不应解释为 203 个坏字体。
- 本次 1,695 个 face 的 `table_errors` 均为空，未发现 name/OS2/head 等表读取错误。
- 旧 README 中的“613 项、扫描错误 0”来自 2026-11-10 的较早目录树，不是这份 2026-11-12 原始扫描的统计。

## 三、57 个无 Unicode cmap 的字体面

57 个 face（涉及 45 个文件）没有找到 Unicode cmap 子表。它们可能是旧式编码字体；即便 Family/PS Name 可读，也不能据此保证 Windows/libass 能按 Unicode 文本正常匹配和显示。

逐项见 [no-unicode-cmap-faces.csv](inventory/no-unicode-cmap-faces.csv)。203 个恢复面见 [recovered-cmap-faces.csv](inventory/recovered-cmap-faces.csv)。

## 四、40 个 ASS 字体候选与 1,061 文件库存的对照

本次使用 ASS 字体名及候选别名，对照 1,695 个 face 的内部名称记录，而非只匹配文件名。结果：

- **31 项找到精确内部名称**：这些字体已经在原始文件夹中，不要因为旧清单而重复下载。
- **8 项精确名称未检出**：另有同族但不同字重／系列的，已在备注中指出。
- **1 项 Arial 不在该字体文件夹**：先确认播放电脑系统字体，不将其作为需要采购或下载的缺口。

| 候选 | 优先级 | 判断 |
|---|---|---|
| 森泽UD新黑 Gb4 R | P1 | 本次 1,061 文件库存未检出精确名称；同族 Gb4 M 已存在；R 字重未检出，不能用 M 代替。 |
| 方正胖娃_GBK | P2 | 本次 1,061 文件库存未检出精确名称；精确 family/full/PostScript/name-table 名称未检出；样本角色为 NextTitle。 |
| FOT-CookHand Std R | P2 | 本次 1,061 文件库存未检出精确名称；精确名称未检出；目前证据用途为 ED/手写效果，不是主对白。 |
| FOT-UDMarugo_Large Pr6N E | P2 | 本次 1,061 文件库存未检出精确名称；同家族 B 字重已存在；E 字重未检出，不能以 B/DB 替代。 |
| Arial | P2 | 文件夹未见；先检查 Windows 系统字体；不在该字体文件夹；先检查播放机器上的 Windows 系统字体，不建议仅因此单独下载。 |
| A-OTF Kocho Std Heavy | P3 | 本次 1,061 文件库存未检出精确名称；Kocho Std Heavy 未检出；不要用其他 A-OTF Heavy 家族代替。 |
| Kozuka Mincho Pr6N M | P3 | 本次 1,061 文件库存未检出精确名称；目录有 Kozuka Mincho 其他系列/字重，但精确 Pr6N M 未检出。 |
| Kozuka Gothic Pro R | P3 | 本次 1,061 文件库存未检出精确名称；目录有 Kozuka Gothic Pro L、Kozuka Gothic Pr6N H 等邻近款，精确 Pro R 未检出。 |
| FA 隷書Ｍ | P3 | 本次 1,061 文件库存未检出精确名称；精确 family/full/PostScript/name-table 名称未检出。 |

逐项文件名、face index、Family、Full Name、PostScript、OS/2 Weight Class 和 cmap 状态：[ass-font-inventory-comparison.csv](inventory/ass-font-inventory-comparison.csv)。

“未检出”只代表这次扫描文件夹里没有精确内部名称匹配；不是 Windows 全局字体状态，也不意味着可用相近家族随意替代。

## 五、原先缺口清单中需要撤销的误判

下列大类在旧清单中曾被列为未见或待确认，但实际已在此次库存中找到：

- Dream Han Sans/Serif：各 27 个字重文件（Sans 当前库存包含 W1–W27 中除 W12/W22 外的字重；Serif 包含 W1–W27 中除 W7/W20 外的字重），包含 SC/TC/HC/J/K；ASS 样本点名的 Sans W20、Serif W14 等存在。
- Swei Gothic CJK SC/TC Medium、Bold、Black 六个版本；Resource Han Rounded CN Bold。
- LXGW WenKai Medium/Bold/GB Medium/TC Medium、Marker Gothic、ZhenKai、ZhenKai Slab；小赖、悠哉未检出。
- 文泉驿点阵宋体 12/13/14/15px；16px 未检出。
- 汉仪正圆 35/55/65/75/85/95S、汉仪玄宋 35/45/55/65/75/85/95S 和若干汉仪旗黑字重。
- 多款方正、FOT、A-OTF、华康款式，详见新版 [FONT_GAP_LIST.md](FONT_GAP_LIST.md)。
- 851 手書き雑フォント、MuzaiPixel、CLFN 24x CN、Koku Mincho、猫啃什锦黑 Lite、奶布儿蝴蝶体、也字工厂幼稚园体和腾祥嘉丽准粗圆。

## 六、仍然不能据此断言的事情

1. 这是原始 `font for mpv` 目录的全量快照，不是后来整理的 51 文件 Core/Optional 精选包。精选包此前终端记录为 41 Core + 10 Optional，但仓库没有它最终的 `manifest.csv`，所以不能声称 51 包具体含有或缺少哪些字体。
2. 元数据可读不代表每个字形完整，也不模拟 Windows DirectWrite、mpv/libass 的字体匹配、CJK 地区字形 fallback。
3. 尚未用用户的 mpv 对真实 ASS 播放验证，也未做逐码点覆盖检查。
4. 仓库只记录名称、扫描元数据和研究结果；未上传商业字体二进制。

## 七、数据入口

- 原始扫描：[font_inventory_20261112_151422.csv](font_inventory_20261112_151422.csv)、[JSON](font_inventory_20261112_151422.json)、[日志](font_scan_errors_20261112_151422.txt)
- ASS 字体对照：[inventory/ass-font-inventory-comparison.csv](inventory/ass-font-inventory-comparison.csv)
- 无 Unicode cmap：[inventory/no-unicode-cmap-faces.csv](inventory/no-unicode-cmap-faces.csv)
- cmap 恢复诊断：[inventory/recovered-cmap-faces.csv](inventory/recovered-cmap-faces.csv)
- 人工可读缺口表：[FONT_GAP_LIST.md](FONT_GAP_LIST.md)
