## Windows 免安装字体扫描工具

- **[下载 FontNameInspector-Portable.zip](https://github.com/WuLinLee/just/releases/download/windows-portable-latest/FontNameInspector-Portable.zip)**：解压后双击 EXE。
- [直接下载 EXE](https://github.com/WuLinLee/just/releases/download/windows-portable-latest/FontNameInspector.exe)
- [云编译结果](https://github.com/WuLinLee/just/actions/runs/43162222972)
- [工具使用说明](./tools/README_免安装使用.md)

# mpv / ACG 字幕字体库存与缺口

本仓库记录 `E:\mpv-lazy\font for mpv` 原始字体目录的内部名称扫描、字幕组 ASS 字体证据和建议补充项。

## 当前库存基准

最新完整扫描来自 **2026-11-12 15:14 (+08:00)**，不是旧清单里的 613 项目录树：

- **1,061 个字体文件**
- **1,695 个字体 face**（TTC/OTC 每个内嵌 face 单独计数）
- 1,435 个 cmap 正常；203 个 cmap 容错恢复；57 个 face 无 Unicode cmap 子表
- 203 条 TXT 日志均为 cmap 恢复诊断，不是 203 个完全读取失败的字体；name/OS2/head 表错误为 0。

详细报告：[FONT_INVENTORY_AUDIT.md](./FONT_INVENTORY_AUDIT.md)。原始数据：[CSV](./font_inventory_20261112_151422.csv) · [JSON](./font_inventory_20261112_151422.json) · [扫描日志](./font_scan_errors_20261112_151422.txt)。

## 现在到底还缺什么？

已将 40 个公开 ASS 字体候选按字体内部名称与原始库存逐项对照：**31 项精确存在、8 项未检出、Arial 1 项需检查 Windows 系统字体**。

- [最新缺口总表](./FONT_GAP_LIST.md)
- [ASS × 库存逐条匹配 CSV](./inventory/ass-font-inventory-comparison.csv)
- [无 Unicode cmap 的 57 个 face](./inventory/no-unicode-cmap-faces.csv)
- [203 个 cmap 恢复记录](./inventory/recovered-cmap-faces.csv)
- [UD Digi Kyokasho N-R 官方安装与授权说明](./UDDigiKyokashoN-R.md)

优先核对项：森泽UD新黑 Gb4 R；随后是方正胖娃、FOT-CookHand Std R、FOT-UDMarugo Large Pr6N E；Kocho/Kozuka/FA 隷書属于低频标题或画面字。具体用途和状态见缺口清单。

## 重要口径：别把三个库存混为一谈

1. **1,061 文件 / 1,695 face**：2026-11-12 原始 `font for mpv` 目录扫描。
2. **613 项目录树**：2026-11-10 的较早文件名清单，不能替代最新内部名称扫描。
3. **51 文件精选包**：此前输出 41 Core + 10 Optional；最终 manifest 尚未进入仓库，所以尚未完成精选包级别的差集。

## ASS 字幕组研究

多字幕组公开 ASS 的样本、角色分析和提取脚本在 [new 分支研究目录](https://github.com/WuLinLee/just/tree/new/research/subtitle-group-ass-font-audit)。其中区分主对白与 OP/ED、标题、Staff、屏幕字，不把 VCB 发布标记直接当作字幕制作组。

## 授权与文件

本仓库只保存工具、字体名称、扫描元数据、来源链接和研究结果。**不上传商业字体二进制或未经授权的字幕文件**。开源字体也需遵守各自许可证和版权声明。

## ASS 字幕组研究资料（new 分支）

- [研究总览](./research/subtitle-group-ass-font-audit/README.md)
- [34 个 ASS 样本来源](./research/subtitle-group-ass-font-audit/data/ass-samples.csv)
- [40 项 ASS 候选字体及库存状态](./research/subtitle-group-ass-font-audit/data/font-candidates.csv)
- [ASS 字体 × 原始库存逐项对照](./research/subtitle-group-ass-font-audit/data/ass-font-inventory-comparison.csv)
- [交接给下一位 AI](./research/subtitle-group-ass-font-audit/HANDOFF_NEXT_AI.md)

当前 ASS 对照针对原始 1,061 文件库；51 文件 Core/Optional 精选包仍待 manifest。
