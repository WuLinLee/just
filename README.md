## Windows 免安装字体扫描工具（已云编译）

- **[下载 FontNameInspector-Portable.zip](https://github.com/WuLinLee/just/releases/download/windows-portable-latest/FontNameInspector-Portable.zip)**：解压后双击 EXE 即可使用；无需在本机安装 Python、pip 或 FontTools。
- [直接下载 EXE](https://github.com/WuLinLee/just/releases/download/windows-portable-latest/FontNameInspector.exe)
- [查看云编译结果](https://github.com/WuLinLee/just/actions/runs/43162222972)
- [工具使用说明](./tools/README_免安装使用.md)

# mpv / ACG 字幕字体缺口清单

本仓库用于记录对照你上传的 `E:\\mpv-lazy\\font for mpv` 字体目录后，值得补充的动漫／影视字幕字体。

## 先看这里

- [打开完整缺失清单：FONT_GAP_LIST.md](./FONT_GAP_LIST.md)
- [UDDigiKyokashoN-R.ttc：微软官方获取方式与授权说明](./UDDigiKyokashoN-R.md)
- 清点基准：你提供的目录树，共 **613 个文件条目**，扫描错误 **0**。
- 对照方法：按目录中的文件名与字幕组公开字体需求逐项比对；对缩写名、TTC 集合字体和内部 PostScript 名称无法仅凭文件名确认的项目，已标为“待核验”，没有擅自算作确定缺失。
- 当前仓库**只提交了字体名称、差异说明、社区来源和官方获取链接，没有提交字体二进制文件**。商业字体不能在没有再分发授权的情况下镜像；开源字体也必须连同许可证和版权声明分发。本次提交渠道未能将上游二进制字体文件安全转存到本仓库，因此开源字体请从清单中的作者官方仓库／Release 获取。

## 比对结论

你现有的基础字库已经很充足：方正、华康、日文字体、思源黑体／宋体、更纱黑体都有相当多的版本。最值得新增的不是重复下载普通黑体，而是：

1. **梦源黑体／梦源宋体**的多级字重（SC／TC／J），这是近年字幕清单中很明显的一块缺口。
2. **獅尾圓體、Resource Han Rounded**等不同圆体家族。
3. **霞鹜文楷、霞鹜漫黑、霞鹜臻楷、小赖、悠哉、得意黑、朱雀仿宋**等与现有方正／华康字体风格不同的开源字型。
4. 已有字体家族中缺少的特定字重或特殊款，例如 FOT、A-OTF、汉仪正圆，以及部分方正字体。

## 重要提醒

社区字幕清单代表“作品字幕实际引用过”，不等于所有字体都免费或允许公开再分发。请优先从作者／字库厂商的官方渠道获取，并按各字体许可证使用。
