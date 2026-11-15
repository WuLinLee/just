# mpv / ACG 字幕字体：基于完整内部名称扫描的缺口清单

> **最新可用库存快照：2026-11-12 15:14（+08:00）**
> 原始目录：`E:\mpv-lazy\font for mpv`
> **1,061 个字体文件、1,695 个字体 face**。本表已从旧的“613 项目录树文件名初筛”升级为对照字体内部名称的结果。

## 先看结论

你原始 `font for mpv` 文件夹的字体库比旧清单显示的更齐全。旧清单里不少项目只是文件名不明显，实际存在于 TTC 的某个 face，或存在于字体内部英文/日文名称记录里。

对 40 个已研究 ASS 字体候选，当前原始库存中：
- **31 项找到精确内部名称**，无需重复下载。
- **8 项未检出精确名称**，其中有些只是同一家族缺某一字重／系列。
- **Arial 1 项不在该文件夹**，但应先检查 Windows 系统字体。

完整可筛选的对照表：[ASS 字体 × 原始库存匹配 CSV](inventory/ass-font-inventory-comparison.csv)。扫描统计与判定方法：[全量库存审计报告](FONT_INVENTORY_AUDIT.md)。

**注意：**这不是 51 文件 Core/Optional 精选包的差集。51 包仍缺最终 manifest；不要把 1,061 文件原始库的“已存在”自动映射成 51 包已存在。

---

## A. 真实 ASS 样本候选里，当前最值得补的

### P1：优先核对
| 字体 | 当前结果 | 为什么值得补 |
|---|---|---|
| 森泽UD新黑 Gb4 R | **未检出精确 R 字重**；Gb4 M 已有 | 与简体中文字体需求有关；M 不能完全代替 R |

### P2：作品专用字／歌词／标题
| 字体 | 当前结果 | 角色 |
|---|---|---|
| 方正胖娃_GBK | 未检出 | 《Endro》NextTitle 预告标题 |
| FOT-CookHand Std R | 未检出 | OP/ED／手写效果，不是主对白 |
| FOT-UDMarugo_Large Pr6N E | 未检出；同族 B 已有 | 项目字体需求；需精确字重 |

### P3：低频装饰／屏幕字
| 字体 | 当前结果 | 角色 |
|---|---|---|
| A-OTF Kocho Std Heavy | 未检出 | Logo |
| Kozuka Mincho Pr6N M | 未检出；其他 Kozuka Mincho 款已存在 | 竖排画面字 |
| Kozuka Gothic Pro R | 未检出；Pro L / Pr6N H 等邻近款已存在 | 竖排画面字 |
| FA 隷書Ｍ | 未检出 | OP 日文歌词 |

### 系统字体，不建议当作下载缺口
- **Arial**：这次在自带目录里没找到；先检查 Windows `C:\Windows\Fonts`、Font Settings 和 mpv 实际运行环境。Windows 常见系统字体不在自定义目录，不代表机器一定缺失。

商业字体（方正、汉仪、华康/DFP、Fontworks、Morisawa、Adobe 等）须按具体产品和用途获取授权；这里只列名称，不提供未经授权的字体包。

---

## B. 之前被列为缺失、实际已在原始库存里的字体

### 1. 梦源黑体／梦源宋体：不要整套重下

原始库中：
- Dream Han Sans：27 个 TTC 字重文件，SC/TC/HC/J/K 多地区 face 齐全；ASS 用到的 **SC W20、J W20 已有**。
- Dream Han Serif：27 个 TTC 字重文件，SC/TC/HC/J/K 多地区 face 齐全；ASS 用到的 **SC W14、J W14 已有**。
- Sans 当前见到 W1–W27 中除 W12、W22 以外的字重；Serif 当前见到 W1–W27 中除 W7、W20 以外的字重。

### 2. 已有的开源/圆体/手写系列

| 字体家族 | 扫描到的内容 |
|---|---|
| 獅尾圓體 Swei Gothic | SC/TC Medium、Bold、Black |
| Resource Han Rounded | CN Bold |
| 霞鹜文楷 LXGW WenKai | Medium、Bold、GB Medium、TC Medium |
| 霞鹜漫黑 LXGW Marker Gothic | Regular |
| 霞鹜臻楷 LXGW ZhenKai | Regular，以及 ZhenKai Slab GB |
| 文泉驿点阵宋体 | 12px、13px、14px、15px；16px 未检出 |
| 851 手書き雑フォント | 已有 |
| MuzaiPixel | 已有 |
| CLFN 24x CN | 已有 |
| Koku Mincho Regular | 已有 |

以下旧清单中列为待下载的开源字体，仍未在本次扫描中找到：**小赖字体 Xiaolai、悠哉字体 Yozai、得意黑 Smiley Sans、朱雀仿宋 Zhuque Fangsong、文泉驿点阵宋体 16px**。如果确实需要它们，再从作者官方项目页获取；不要从第三方字体合集转存。

官方来源：
- Dream Han：[Pal3love/dream-han-cjk](https://github.com/Pal3love/dream-han-cjk/releases)
- Swei Gothic：[max32002/swei-gothic](https://github.com/max32002/swei-gothic)
- Resource Han Rounded：[CyanoHao/Resource-Han-Rounded](https://github.com/CyanoHao/Resource-Han-Rounded/releases)
- LXGW WenKai：[LXGW WenKai Releases](https://github.com/lxgw/LxgwWenKai/releases)
- LXGW Marker Gothic：[LXGW Marker Gothic](https://github.com/lxgw/LxgwMarkerGothic/releases)
- LXGW ZhenKai：[LXGW ZhenKai](https://github.com/lxgw/LxgwZhenKai/releases)
- Xiaolai：[kose-font](https://github.com/lxgw/kose-font/releases)
- Yozai：[yozai-font](https://github.com/lxgw/yozai-font/releases)
- Smiley Sans：[Smiley Sans](https://github.com/atelier-anchor/smiley-sans/releases)
- Zhuque：[Zhuque](https://github.com/TrionesType/zhuque/releases)
- WenQuanYi Bitmap Song：[官方项目](https://github.com/AmusementClub/WenQuanYi-Bitmap-Song-TTF)

### 3. 方正系列：大部分旧候选其实已存在

**已找到：**
- 方正屏显雅宋、方正北魏楷书、方正筑紫明朝宋；
- 方正FW珍珠体、方正FW童趣POP体、方正达利体；
- 方正榜书楷、方正榜书行、方正莎儿硬笔、方正雅士黑；
- 方正喵呜、方正卡通、方正少儿、方正中倩、方正宋黑、小标宋、书宋；
- 方正兰亭圆 DB 与 DB1 两个不同字重；
- 方正锐正黑目前见到 Bold、DemiBold，不能据此认定 Regular/ExtraBold 也齐全。

**仍未检出：**
- 方正标雅宋、方正细雅宋、方正特雅宋；
- 方正字迹－杨素彬楷、方正流行体；
- 方正胖娃_GBK（ASS 候选，见 A 节）。

方正官方查询：[方正字库](https://www.foundertype.com/)。

### 4. 汉仪：指定字重基本已覆盖

- 汉仪正圆：35S、55S、65S、75S、85S、95S 均找到。
- 汉仪玄宋：35S、45S、55S、65S、75S、85S、95S 均找到。
- 汉仪旗黑：45S、50S、65S、75S、85S、95S、105JF 等多个字重找到。
- 汉仪风波便利店 W、汉仪歪歪体简也找到。

不要再按旧清单整套下载汉仪正圆／玄宋／旗黑。具体内部名见 [ASS 对照 CSV](inventory/ass-font-inventory-comparison.csv) 与原始 inventory CSV。

官方查询：[汉仪字库](https://w.hanyi.com.cn/font-list)。

### 5. Fontworks / FOT：多款指定字重已存在

已找到：
- FOT-TelopMin ProN B/E；
- FOT-TsukuAOldMin Pr6N R，以及 Pr6 M、Pr6N D；
- FOT-TsukuMin Pr6N L/B 和其他字重；
- FOT-NewRodin ProN B/DB；
- FOT-Skip Std B/D/E/L/M；
- FOT-MatisseV Pro B；
- FOT-Kurokane Std EB；
- FOT-Pearl Std L；
- FOT-NewCezanne Pro / ProN B、DB；
- FOT-UDKakugo Large Pr6N B/R。

仍未检出：
- FOT-CookHand Std R；
- FOT-UDMarugo Large Pr6N E（B 已有）。

官方获取：[Fontworks](https://fontworks.co.jp/)。

### 6. Morisawa / A-OTF：旧清单中的四个候选都已找到

- A-OTF Antique Std AN4；
- A-OTF Futo Go B101 Pr6N Bold；
- A-OTF Ryumin Pr6N B-KL；
- A-OTF Shin Maru Go Pr6N DB。

另外，Morisawa **MO UDShinGo SC Gb4 M** 与 **A-OTF UD Shin Go Pr6N M** 是两个不同家族、两款字体；两者在原始库中都存在。MO UDShinGo SC Gb4 R 未检出。

官方获取：[Morisawa](https://www.morisawa.co.jp/)。

### 7. 华康／DFP：多数存在，少数精确款未检出

已找到：
- DFP-POP Mix W5；
- 华康楷书 W7（含 DFP/P face）；
- 华康圆体 W7-A、华康方圆体 W7(P)；
- 华康翩翩体 W3-A/W5-A、华康少女文字 W5。

未检出：
- DFP-京劇体 W5；
- 华康正颜楷体 W7。

官方查询：[华康字型](https://www.dynacw.com.cn/index.aspx)。

### 8. 其他旧候选

已找到：仓耳今楷 01-27533 W04、仓耳今楷 01 W05、仓耳今楷 04 W04、猫啃什锦黑 Lite、奶布儿蝴蝶体、也字工厂幼稚园体、腾祥嘉丽准粗圆。

未检出：仓耳今楷 03 W04、喜鹊乐敦体。

---

## C. 扫描数据质量：不要把警告误认为坏字体

这次全量扫描的 1,695 个 face 中：
- 1,435 个 cmap 正常解析；
- 203 个 cmap 容错恢复（涉及 75 个文件），不是 203 个无法读取的字体；
- 57 个 face（45 个文件）没有 Unicode cmap 子表，需要特别注意旧编码和 Unicode 显示兼容。

查看：
- [全量库存审计报告](FONT_INVENTORY_AUDIT.md)
- [无 Unicode cmap 的 57 个 face](inventory/no-unicode-cmap-faces.csv)
- [203 个 cmap 恢复记录](inventory/recovered-cmap-faces.csv)
- [原始 CSV](font_inventory_20261112_151422.csv) / [原始 JSON](font_inventory_20261112_151422.json) / [原始日志](font_scan_errors_20261112_151422.txt)

## D. 与 51 文件精选包的区别

此前用户终端记录的精选包是 41 个 Core + 10 个 Optional，总计 51 个文件。它是从原始字体目录另行挑选的子集。当前仓库没有该包最终的 `manifest.csv`，所以本清单只能说明**原始 1,061 文件目录**里有什么，不能说明 51 包里具体保留了哪些文件。

拿到 51 包 manifest 后，才可以做 Core / Optional 的精确差集。

## E. 再分发与授权

- 商业字体：方正、汉仪、华康/DFP、Fontworks、Morisawa、Adobe 等，按具体产品许可获取。这里不上传字体二进制。
- 开源字体：OFL/其他许可证各有条款；再分发时保留许可证和版权声明，并遵守 Reserved Font Name 等条件。
- Windows 随附字体（例如 UD Digi Kyokasho）通过 Windows 可选功能或官方途径获取，不复制或镜像到本仓库。
- 社区字幕文件公开可访问，不代表字体或字幕可以任意再分发。

参考：[OFL 1.1](https://openfontlicense.org/open-font-license-official-text/)；[UD Digi Kyokasho 官方获取说明](UDDigiKyokashoN-R.md)。
