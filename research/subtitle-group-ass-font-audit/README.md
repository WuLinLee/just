# 动漫／影视字幕组 ASS 字体抽样审计

> **2026-11-16 库存复核更新**：已用 2026-11-12 的 Font Name Inspector 全量输出（1,061 个文件 / 1,695 个 face）与 ASS 候选字体做内部 name table 比对。40 项候选中 **31 项已精确找到、8 项未检出、Arial 1 项需检查 Windows 系统字体**。这不是 51 文件精选包差集；51 包 manifest 仍未取得。查看 [完整审计报告](../../FONT_INVENTORY_AUDIT.md)、[逐项对照 CSV](data/ass-font-inventory-comparison.csv)、[无 Unicode cmap 清单](../../inventory/no-unicode-cmap-faces.csv) 与 [cmap 恢复记录](../../inventory/recovered-cmap-faces.csv)。


> 审计日期：2026-11-16  
> 状态：**公开资料抽样、静态 ASS 样本分析及原始 1,061 文件库的内部名称对照已完成首轮；51 文件精选包逐文件差集和 mpv/libass 实机播放仍未完成。**

本目录记录这轮针对多个中文动漫字幕来源的公开 ASS 字幕字体调查，目标是帮助后续研究者回答：

1. 同一字幕组跨作品重复使用哪些主对白字体？
2. 哪些字体只用于歌词、标题、屏幕字、スタッフ表或特效？
3. 与用户此前建立的 51 文件精选字体包相比，哪些是值得核验／补充的字体？
4. 下一个 AI 应如何继续扩大样本并得出可复现的准确差集？

## 快速入口

- [逐个 ASS／作品样本及来源（CSV）](data/ass-samples.csv)
- [字体候选与核验状态（CSV）](data/font-candidates.csv)
- [结构化字体观察数据（JSON）](data/group-font-evidence.json)
- [ASS 字体提取与审计方法](docs/ass-font-audit-method.md)
- [批量 ASS/SSA 字体提取脚本](scripts/ass_font_audit.py)（Python 标准库）
- [脚本最小测试](tests/test_ass_font_audit.py)
- [交接给下一个 AI 的待办清单](HANDOFF_NEXT_AI.md)

## 重要结论

### 1. 按字幕组归类比按压制发布名归类更准确

VCB-Studio 是常见压制／发布标签，但并不代表所有随包字幕均由 VCB-Studio 制作。本次公开样本中可以看到：

- 《Endro》ASS 的制作字幕署名为**轻之国度字幕组**。
- 《狂赌之渊》特典 ASS 明确出现**悠哈璃羽字幕社**署名。
- 《猫娘乐园》特典 ASS 的注释写有**千夏字幕组**。
- 《NO GAME NO LIFE》特典 ASS 的 `Original Script` 写明 **SumiSora**。
- 《可塑性记忆》文件名为 KTXP&VCB 合作发布，不能仅由文件名推导具体字体由哪一方制定。

后续分析必须区分：字幕制作署名、原始字幕来源、合作组、压制发布者、文件名标签。

### 2. 同一来源会重复使用部分基础字体，但每部作品仍可能扩展字体

跨作品样本显示一些可复用的习惯，例如：

- **喵萌奶茶屋**公开 ASS 中，《犬与猫》样本用 `FZZhunYuan-M02`；《Touhai／斗牌》样本用 `FZLanTingYuan-DB-GBK`，スタッフ样式还出现 `HYXuanSong 75S`。喵萌不同作品的 README 字体表则反复出现方正准圆、兰亭圆、少儿，以及汉仪、华康和 FOT 字体。
- **SweetSub**《Sarazanmai》多份预览 ASS 使用 `Source Han Sans SC Medium` 作为主字幕字体、`Source Han Serif SC SemiBold` 作为另一类样式；《Koori no Jouheki》则用 `Dream Han Sans SC W20` 和 `Dream Han Sans J W20` 作为中文／日文样式，并配套梦源宋体。
- **MingYSub**《前辈是男孩子》ED 样本使用 `森泽UD新黑 Gb4 M`、`华康翩翩体W5-A`、`FOT-CookHand Std R`；《街角魔族 2 丁目》样本也出现森泽 UD 新黑和 A-OTF UD Shin Go。
- **轻之国度**《Endro》多集样式重复使用 `方正兰亭中黑_GBK` 作为主对白／注释字体；标题另外用方正少儿、方正胖娃。
- **北宇治**《孤独摇滚》多集 ASS 中，OP／ED 样式反复出现方正卡通、方正喵呜、Aunt-香堇体等；这些是歌词／标题样式，不应误算成正片主对白字体。
- **千夏**《猫娘乐园》特典样本主对白为 `华康圆体W7-A`，中日歌词使用其他字体。
- **LoliHouse**《少女☆歌剧 Revue Starlight》剧场版样本以思源黑体／宋体字重构建对白和歌词样式。

因此，不能把一个 ASS 的所有 Style 字体简单视作“主对白必装字体”。样式名称和事件用途必须结合起来判断。

### 3. 原始 1,061 文件库的已存在与未检出项

已确认存在的高优先级字体包括 Dream Han Sans SC/J W20、Dream Han Serif SC/J W14、华康圆体W7-A、华康方圆体W7(P)、森泽UD新黑 Gb4 M、A-OTF UD Shin Go Pr6N M、Source Han Sans SC/TC Medium、Source Han Serif SC/TC SemiBold 等。

40 项 ASS 候选的逐项结果在 [ass-font-inventory-comparison.csv](data/ass-font-inventory-comparison.csv)。当前精确未检出的 8 项：
- 森泽UD新黑 Gb4 R（同族 M 已有，但不是同一字重）
- 方正胖娃_GBK
- FOT-CookHand Std R
- FOT-UDMarugo_Large Pr6N E（同族 B 已有）
- A-OTF Kocho Std Heavy
- Kozuka Mincho Pr6N M（同目录有其他 Kozuka Mincho 变体）
- Kozuka Gothic Pro R（有相邻系列/字重）
- FA 隷書Ｍ

另有 Arial 不在自带目录，先检查 Windows 系统字体。完整匹配文件名、face、内部名称和 cmap 状态见逐项 CSV。## 与已有字体包和本仓库既有清单的关系

请特别区分以下三个集合：

1. **本次字幕组审计所见字体**：来自公开 ASS 的样式名和行内字体覆盖标签，以及字幕项目 README 的字体需求列表。
2. **用户此前建立的 51 文件 mpv 精选包**：用户此前运行脚本成功，终端报告 41 个核心文件、10 个可选文件，共 51 个，大小约 662.5 MB。对话摘要只保留了部分字体家族信息；当前研究没有取得该精选包的完整 `manifest.csv` 和 51 个文件的内部 name table。
3. **仓库 main 分支已有的 FONT_GAP_LIST.md**：该清单基于另一份用户字体目录树（613 个文件条目，清单日期 2026-11-10），不是 51 文件精选包的 manifest。

这三个基准不能合并计算。**本目录中的“候选缺口”不是已经完成的逐文件差集**。在取得 51 文件 manifest 或字体包之前，不能把“没有出现在本轮对话摘要中”写成“已确认缺失”。

## 批量解析辅助脚本

在研究目录内执行（Python 3.10+，无第三方依赖）：

```bash
python scripts/ass_font_audit.py --input /path/to/subtitle-folder
python scripts/ass_font_audit.py --input /path/to/example.ass --output-dir ./audit-output
python -m unittest discover -s tests
```

默认递归扫描 `.ass`／`.ssa`，输出 `ass_font_audit.json` 与 `ass_font_audit.csv`。脚本把“Style 已定义”和“被 Dialogue 使用”分开计数，并提取行内 `\\fn`、`\\r` 与 ASS `[Fonts]` 段名称。它不是 libass 渲染器，也不解析 MKV/MKS 容器附件；解析结果仍需人工复核。

## 审计边界

- 样本是公开仓库当前可访问的 ASS／字幕项目字体说明；不代表完整扫描了各字幕组所有年份和所有作品。
- 只提取字体名称、样式名、署名与必要的简短证据；没有把字幕文件全文或字体二进制复制到本仓库。
- `\fn` 行内覆盖可能改变字体；同一 style 也可能被 `\r` 重置；必须解析 Events 才能识别真实使用集合。
- ASS 样式定义的字体可能没有被任何 Dialogue 行调用；未使用样式不应自动列为必需字体。
- MKV／MKS 可能内嵌字体；内嵌字体不等于本机字体库缺失。
- 字体族相近不代表字体文件、字重、内部 PostScript 名称或字符覆盖一致。
- 没有运行 mpv/libass 播放验证；字符覆盖也没有通过用户的真实字体文件逐码点检验。

## 来源与再分发

每个数据行都带有直接来源链接。优先使用字幕组官方仓库；第三方聚合仓库（例如 bipy/Anime-Subtitles）用于交叉检索和定位公开 ASS，来源属性按 ASS 内部署名注明。

本分支**不包含商业字体文件、字体包、字幕二进制附件或未经授权的素材**。这里只提交审计数据、字体名称、来源 URL 和可复现方法。公开字幕仓库自身的转载许可仍需遵守；不因可下载就推定可修改或再分发。

## 推荐下一步

1. 获取用户实际 51 文件精选包的 `manifest.csv`。
2. 用本仓库现有 FontNameInspector 读取 51 个文件的 Family、Full Name、PostScript Name、Typographic Family、字重和 TTC face index。
3. 从 CSV 的来源链接扩充更多同一字幕组跨作品样本；优先采集主对白 ASS，而非仅采集 OP／ED。
4. 抽取 Style、Events 中的 `\fn`、`\r`，识别未使用 style、实际字体覆盖和嵌入字体。
5. 生成可复现的精确差集，并使用真实 mpv 播放验证。

更多细节见 [HANDOFF_NEXT_AI.md](HANDOFF_NEXT_AI.md)。
