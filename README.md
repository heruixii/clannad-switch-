# CLANNAD Nintendo Switch 简体中文汉化（ALTIRKIE）

[![版本](https://img.shields.io/badge/CLANNAD-v1.0.7-blue)](https://github.com/heruixii/clannad-switch-/releases) [![最新修复](https://img.shields.io/badge/汉化-fix10-success)](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)

这是《CLANNAD》Nintendo Switch 版的**简体中文移植汉化工程**。文本来源为既有 PC 版《CLANNAD FV 汉化补丁 2.0》，Switch 移植汉化：**ALTIRKIE**。

**目标游戏版本：v1.0.7**　·　**Title ID：`0100A3A00CC7E000`**　·　当前发布：**fix10（2026-10-14）**

> **新用户注意：fix10 是升级修复包，不是独立的全量包。** 必须先安装 [fix8 完整汉化包](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix8)，再安装 [fix10 升级修复包](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)。已经完整安装 fix8/fix9 的用户只需按下文升级。

## 最新修复：fix10

先前部分存档会在 **4 月 14 日春原宿舍录音机剧情**附近闪退，Atmosphère 报告显示 `MakeTextThread` 异常。定位后确认：LucaSystem 剧情回编时文本长度变化，但一些 `GOTO`/条件分支/跨场景跳转仍保留旧的绝对地址。

- 解析 **213 个场景脚本**，重定位 **170 个场景中的 6,566 个跳转地址引用**；原始中文译文不变。
- 保持已验证的中文 `FONT.PAK`，ExeFS 使用仅一份 **fix9 IPS**，继续支持菜单、设置、主角姓名等功能。
- **实机已验证**：使用 No.1 旧存档推进春原录音机及后续日期不再闪退；中文字库、菜单、设置、姓名等显示正常。
- **验证范围限制**：尚未逐条完成所有角色路线及 After Story 的全流程通关，不能保证所有可能路径均不存在其他独立问题。

下载：[**v1.0.7-fix10 GitHub Release**](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)（ZIP 约 205 MB）

## 卸载旧版并升级 fix10

**操作前彻底退出游戏，备份存档和 SD 卡上现有汉化文件。不要删除游戏本体或存档。**

1. 确认游戏版本为 **v1.0.7**，且 Atmosphère 能正常启动游戏。
2. 在 SD 卡 `atmosphere/exefs_patches/` 中，找出所有 `CLANNAD_CHS_*` 旧文件夹（fix3～fix9 等），**先复制到 SD 卡根目录以外的备份位置或电脑，再移出 `exefs_patches`**。不要同时留下两个针对同一个 Build ID `CF38595316BAA425E792CE5CD122DFC6` 的有效 `.ips`。
3. 进入 `atmosphere/contents/0100A3A00CC7E000/romfs/`，备份原 `SCRIPT.PAK` 和 `FONT.PAK`。**保留**先前完整汉化提供的 `MANUAL.PAK`、`OTHCG.PAK`、`PARTS.PAK`、`PARTS2.PAK`、`SYSCG.PAK`，不要删除这些文件。
4. 下载 [fix10 升级包](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)，解压并将其内部的 `atmosphere` 文件夹复制到 SD 卡根目录，合并文件夹，允许覆盖 `SCRIPT.PAK` 和 `FONT.PAK`。
5. 完成后检查：`romfs` 内是 **7 个汉化 PAK**；`atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix9/` 内只有 **1 份**匹配 Build ID 的 IPS；**不要再启用 fix3～fix8 IPS**。这是 fix10 的正常结构：组合包沿用 fix9 的 ExeFS 二进制文件。
6. 完全重启 CLANNAD，读取原有存档，检查剧情、标题菜单、设置、主角姓名和中文字体。

如果你是**首次安装**：先安装 [fix8 完整包](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix8) 以获得七个 RomFS 资源，再执行以上步骤安装 fix10。**只解压 fix10 不能替代完整 fix8 的全部 UI、手册和图片资源。**

更详细的升级、完全卸载与回退方案见 [fix10 安装及排错文档](汉化工作/docs/06-fix10-升级卸载与排错.md)。

## 如何彻底卸载汉化（恢复原版）

先备份、关闭游戏，再将 `atmosphere/exefs_patches/` 下**仅属于 CLANNAD** 的 `CLANNAD_CHS_*` 目录移出或删除，并将 `atmosphere/contents/0100A3A00CC7E000/romfs/` 中已安装的汉化资源文件移出或删除。若该 Title ID 下还有你自己安装的其它 Mod，只移除汉化覆盖文件，不要误删其他内容。

**无需卸载游戏本体、更新或删除存档。** 若不确定哪些文件属于汉化，先移至电脑备份，不要永久删除。

## 汉化范围

本篇、各角色路线、**After Story（后日谈）**剧情、剧情选项、标题与系统菜单、设置页面、团子百科、主人公姓名、中文字体及相关 UI/手册文本。部分 logo、商标和控制器键位符号保留原样。

## 工程、贡献与版权说明

仓库主要提供翻译工程元数据、构建/校验脚本、使用说明以及相关修复分析。编译脚本中的跳转修复可通过 [fix10 重新定位工具](汉化工作/04_scripts/rebase_script_absolute_branches_fix10.py) 重现，必须使用者合法取得的原有 `SCRIPT.PAK`，并验证源文件校验值。

- 原作：KEY / VisualArt's。
- PC 中文译文基础：CLANNAD FV 汉化补丁 2.0；现有资料中未能核实的原 PC 汉化组成员不作杜撰。
- Nintendo Switch 移植汉化与本次修复：**ALTIRKIE**。详见 [贡献与署名](汉化工作/docs/03-贡献与署名.md)。
- 仓库不包含游戏本体、密钥或官方游戏安装文件；Release 的 fix10 仅针对已安装汉化的升级操作。使用时应自行遵守软件许可和当地法规。

## 发布与问题反馈

- [fix10 升级修复](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)（当前版本，优先使用）
- [fix8 完整安装基线](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix8)（首次安装时需要）
- [fix9 历史诊断热修复](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix9-test)（已由 fix10 组合取代，不建议单独使用）

若遇到未覆盖的崩溃，请附游戏版本、哪个存档/日期/剧情、实际生效的 IPS、截图以及 Atmosphère 的 crash report；保留原存档以便重现。
