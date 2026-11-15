# ASS 字体审计方法（供后续 AI／脚本复现）

## 1. 目标

不能只抽取 `[V4+ Styles]` 所有 `Style:` 行就得出缺失字体结论。审计至少要回答：

- ASS 定义了哪些字体？
- 哪些 Style 真正被 Dialogue 事件使用？
- 哪些 Dialogue 在行内用 `\fn字体名` 改过字体？
- 哪些行用 `\r[样式名]` 重置样式？
- 字体用在哪：中／日／英对白、注释、工作人员信息、OP、ED、标题、屏幕字、画面特效？
- 字体是否已经嵌入 ASS 的 `[Fonts]` 段或随 MKV/MKS 封装？

## 2. 提取顺序

本目录提供了一个 Python 标准库脚本 `scripts/ass_font_audit.py`，可先批量生成初始 JSON/CSV：

```bash
python scripts/ass_font_audit.py --input /path/to/ass-folder
python -m unittest discover -s tests
```

脚本仅为第一轮静态提取器；涉及转义、复杂变换标签、字体回退和容器附件时仍需要人工或更完整的 ASS/libass 工具核验。

1. 解析 `[Script Info]`，记录 Title、Original Script、Original Translation、Original Editing、Original Timing、视频/项目分辨率。
2. 解析 `[V4+ Styles]` 或旧版 `[V4 Styles]` 的 Format 和 Style 行。按 Format 字段映射，不要假设 Fontname 总是固定列索引。
3. 解析 `[Events]`，建立每条 Dialogue 的 Style、Layer、Start/End、Comment 状态和 Text。
4. 对每一条非 Comment Dialogue：
   - 统计其 Style 引用；
   - 扫描行内覆盖 `\\fn([^\\}]+)`；
   - 扫描 `\\r(?:([^\\}]+))?`，处理重置后的默认样式；
   - 遇到 `\\t(...)` 时检查内部是否包含字体切换；
   - 记录 `\\fe` 字符集提示但不要把它误作字体名。
5. 解析 `[Fonts]`、`[Graphics]`。有内嵌字体时，单独记为 embedded，不作为本机字体库必须补充的缺口。
6. 归一化字体名时只做安全别名映射；保留原始值。不得仅因“圆体”“黑体”“思源”家族相似而合并。
7. 将每个字体按 Style 名和实际 Dialogue 事件内容分类，并对照同组其他作品。

## 3. ASS 样式频率和重要性

建议按以下顺序排序：

- P0：被非 Comment Dialogue 的默认样式用于正片主对白／注释，且跨多个集或作品重复。
- P1：实际用于主对白或双语注释，但样本量少，或仅单作品出现。
- P2：歌词、工作人员表、屏幕字、标题或画面注释。
- P3：单次 Logo、极短装饰文字、过场特效、极少见的日文／英文装饰字体。

不能按整个 Style 清单数量给字体排优先级。应统计事件使用次数、作品数、集数、角色类别和是否有内嵌字体。

## 4. 字幕组归属判断

可靠度从高到低：

1. ASS 注释／Events 直接写明“本字幕由 X 字幕组制作”。
2. `Script Info` 中 `Original Script`、`Original Translation` 等字段明确指向 X。
3. 字幕组官方仓库内的字幕文件路径和 README 项目署名。
4. 合作发布文件名前缀。
5. 压制／发布包名（例如 VCB-Studio）。

第 4、5 项不能自动推导谁负责字幕和字体设计。出现多个来源时应记录为 mixed / uncertain，而不是强行归入一个组。

## 5. 原始 1,061 文件库存与 51 文件精选包的核验

仓库根目录 `font_inventory_20261112_151422.csv/json` 是原始 `font for mpv` 目录的全量快照（1,061 files / 1,695 faces）。本研究的 `data/ass-font-inventory-comparison.csv` 已将 40 个 ASS 候选与这份原始库存的内部名称表做了对照（31 exact present / 8 not found / Arial 需系统字体检查）。

这**不是** 51 文件 Core/Optional 精选包的差集。51 包的 manifest 尚未提供；需要收到 manifest 后独立进行逐文件、逐 face 和内部名称核验。

需要用户提供该包的 `manifest.csv`（或将 51 文件本身上传给可读取字体元数据的工具）。每个字体应比对：

- File name
- Family / Subfamily
- Full Name
- PostScript Name
- Typographic Family / Subfamily
- WWS Family / Subfamily
- OS/2 Weight Class
- TTC / OTC Face Index
- Unicode cmap 覆盖

ASS 的 Fontname 通常按字体内部家族名匹配；文件名不同并不必然代表缺失，文件名相似也不代表同字重。只有内部名称、字形版本和字符覆盖核验后才能改为 confirmed-present / confirmed-missing。

## 6. mpv 实际验证

- 使用真实的外挂 ASS，而不是只看字体表。
- 确认 mpv 的 `sub-fonts-dir` 指向实际字体文件夹。
- 清除误导性的嵌入字体或至少明确标记嵌入状态，避免把 MKV 内嵌字体误认为本机库已覆盖。
- 使用 mpv/libass 的实际渲染对照检查替代字体、字符 fallback、CJK 地区字形和竖排字体。
- 记录 mpv 版本、libass 版本、操作系统、字体目录和字幕文件哈希／来源链接。

## 7. 本轮审计不包含什么

- 未经许可重新发布字幕文件或字体二进制。
- 未对 51 文件包执行逐字节或完整 name table 差集。
- 未声称在用户的 Windows/m​​pv 环境里实机播放验证成功。
- 不把字幕组 README 列出的所有项目字体误作每一集主对白字体。
- 不把 VCB-Studio 文件名前缀自动当作字幕组归属。
