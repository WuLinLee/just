# Handoff：字幕组 ASS 字体审计

本文件让后续 AI 可以接手，而不用重新从头摸索背景。

## 用户目标

用户正在整理 mpv 的动漫／日剧／电影字幕字体库，希望从实际字幕组的 ASS 文件反推高频主对白、注释、歌词、屏幕字及特效字体，先做 51 个文件的精选库，再按真实需求补充。

用户明确偏好：
- 按字幕组交叉检查多部作品，不只看单个作品。
- 分析真实 ASS，而不是只收集论坛“字体需求清单”。
- 区分主对白与 OP/ED、标题、屏幕字、工作人员表和特效。
- 结果写入本仓库的非 main 分支，便于其他 AI 延续。

## 已完成的动作

- 在 `WuLinLee/just` 的 `new` 分支创建本研究目录。
- 收集并抽查多个公开仓库中的 ASS 文件，以及字幕组官方项目 README 字体清单。
- 整理样本来源、字体名、样式角色、制作来源置信度和待核验项。
- 本分支只提交文本／CSV／JSON／Markdown；没有上传商业字体或字幕二进制。
- 没有修改 main 分支原有 README、FONT_GAP_LIST.md 或其他文件。

## 最重要的当前事实

### A. 51 个精选字体文件的真实 manifest 未取得

之前用户运行的 PowerShell 输出：
- 41 个 Core 文件
- 10 个 Optional 文件
- 共 51 个
- Core 396.3 MB，Optional 266.2 MB，总计约 662.5 MB。

对话摘要只保留了部分家族，例如方正兰亭黑／雅宋／圆体、SubSans/SubLan/SubSerif、部分 Fontworks/A-OTF、思源黑体／宋体和手写字体。**没有取得那 51 个文件的完整 manifest.csv、文件名和内部字体 name table。**

因此本目录中的差异只应称为“candidate gap / manifest check required”，不能称为已确认的逐文件缺失。

### B. main 分支的旧 FONT_GAP_LIST 是不同的库存基准

本仓库 main 分支中的 `FONT_GAP_LIST.md` 写明：根据另一份用户字体目录树，统计了 613 个文件条目（清单日期 2026-11-10）。那不是 51 文件精选包。不要用它代替 51 包 manifest。

### C. 归属不能看压制包名猜

本轮发现：
- Endro ASS 明确写轻之国度字幕组制作。
- Kakegurui SP01 ASS 明确写悠哈璃羽字幕社制作。
- Nekopara Today's Neko08 ASS 注释明确写千夏字幕组制作。
- NGNL SP05 `Original Script` 字段明确写 SumiSora。
- Kuzu no Honkai 同时出现 `Original Script: 漫游字幕组` 和 UHA-WINGS 文件后缀，应标记混合来源。
- VCB-Studio 是发布/压制标记，不能直接作为所有 ASS 字体方案的创作者。

## 当前可优先继续研究的字幕组和样本

1. **Nekomoe kissaten**：官方 Storage 仓库有多系列 ASS 和 README。可从犬与猫、Touhai、ODDTAXI、WEP、Doremi、Non Non Biyori、Yuru Camp、Wistoria 等项目扩样。
2. **SweetSub**：官方仓库有多集 ASS。Sarazanmai 可用作思源黑体/宋体 SC/TC 重复样本；Koori no Jouheki 可用作 Dream Han 主对白样本。
3. **MingYSub**：官方 SubtitlesArchive 仓库有 Bocchi、Skip to Loafer、Machikado Mazoku、Painoko、Dorama DIY、mono 等项目。可以区分主对白与歌声字幕。
4. **KitaujiSub**：官方仓库有 Bocchi 多集 ASS；本轮主要确认 OP/ED/标题字体重复，主对白样式还需要完整解析。
5. **轻之国度**：Endro 多集 ASS 可用于跨集比较兰亭中黑主对白和不同标题字。
6. **千夏/Airota**：Nekopara 特典实际 ASS 区分华康圆体主对白、圆方体标题／中文歌词与 DFPMaruMoji 日文歌词。
7. **UHA-WINGS**：Kakegurui 和 Kuzu no Honkai 样本需注意不同源头及后期署名。
8. **LoliHouse**：本轮只有 Revue Starlight Movie 代表性 ASS，需再找其多个 TV/BD 作品后再归纳组级规律。
9. **KTXP**：Plastic Memories 样本是 KTXP&VCB 合作文件，需找到明确字幕制作署名或官方原始字幕。

## 下一步（按顺序执行）

### 1. 取得用户 51 包 manifest

让用户上传：
`mpv-subtitle-fonts-compact/manifest.csv`

如目录仍保留，可另提供：
- `01_Core` 文件名列表
- `02_Optional_Fallback_and_Handwriting` 文件名列表

不要让用户重新运行整个脚本或重新生成字体包。只要现成 manifest 即可。

### 2. 读取字体内部信息

使用仓库现有 FontNameInspector，重点读取：
- Family
- Subfamily
- Full Name
- PostScript Name
- Typographic Family/Subfamily
- WWS Family/Subfamily
- OS/2 Weight Class
- TTC face index
- cmap 覆盖

尤其核验：
- Dream Han Sans/Serif 是否真的不存在；
- MO UDShinGo SC Gb4 M 是否与现有 A-OTF 或其他名称字体混淆；
- 华康圆体、华康方圆体、翩翩体具体版本和字重；
- 汉仪玄宋/正圆具体字重；
- 方正兰亭圆 DB / DB1，方正少儿、胖娃、喵呜等具体内部名称。

### 3. 对每组至少抽取三部作品／多集 ASS

建议优先扩充 Nekomoe、SweetSub、MingYSub、Kitauji、轻之国度、千夏和 UHA-WINGS。每份 ASS：
- 保存 source URL；
- 不要把原始字幕二进制提交到仓库；
- 只保存必要的解析结果；
- 记录是否嵌入字体；
- 按使用的 Dialogue events 分类字体。

### 4. 产生精确差集

建议结果分成：
- confirmed-present
- confirmed-missing
- family-related-but-not-equivalent
- alias/internal-name-uncertain
- system-font-or-fallback
- embedded-in-subtitle
- project-specific-not-core

只把跨多个作品实际承担主对白的字体优先放进 Core。歌词/标题/特效字体放 Optional。

### 5. mpv 实机测试

用户此前还没有确认已修改 mpv.conf。不要声称已经加载 01_Core。测试时记录：
- `sub-fonts-dir`
- mpv 与 libass 版本
- ASS 源
- 字体内部名称匹配结果
- CJK 字符缺字情况
- 实际截图或日志

## 来源许可和数据清理

- 字幕组 README 里写出字体名称，不等于字体可再分发。
- 本仓库只提交研究结果、来源 URL 和工具，不应上传商业字体二进制。
- 各字幕组字幕也有各自的署名／转载条款；不要把 ASS 全文镜像到本仓库。
- 第三方聚合仓库用于检索的样本应明确标记来源，不要冒充官方字幕组仓库。

## 文件导航

- `data/ass-samples.csv`：实际样本与来源
- `data/font-candidates.csv`：字体候选、角色、优先级和核验状态
- `data/group-font-evidence.json`：供后续 AI 直接读取的结构化摘要
- `docs/ass-font-audit-method.md`：提取方法与判断规则
- `README.md`：研究目录总览
