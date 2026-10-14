# GitHub 备份说明

## 目的

该仓库是本地 `D:\switch游戏\个人汉化\clannad` 的**汉化工程源码级备份**，不是完整游戏镜像。

## 为什么不上传整个本地目录

本地 CLANNAD 目录约 41.8 GB，其中包含完整 XCI、PC 版游戏、更新数据、原始/解包 RomFS、官方语音/CG/音乐 PAK 和多个旧版完整发布包。这些文件既不适合公开 Git 仓库，也超过 GitHub 常规文件限制。

因此 GitHub 仅保存可维护、可追溯的汉化工程数据；完整游戏资源继续保留在本地。

## 已纳入备份

- `汉化工作/04_scripts/`：构建、转换、打包、QA 脚本
- `汉化工作/03_text/translated/`：最终译文目标表与 QA 数据
- `汉化工作/03_text/switch_inventory/`：Switch 场景/资源清单元数据
- `汉化工作/docs/`：基线、贡献、使用、复现说明
- `汉化工作/07_archive/scripts_analysis/`：历史分析/定位脚本
- `汉化工作/07_archive/ORGANIZE_20260908.log`：收尾整理记录
- fix8/fix6 ExeFS IPS 与 QA 小型产物（强制加入，虽位于 `05_build`）
- 团子百科最终翻译 JSON/TSV 与 QA
- 最终发布目录中的 README/CREDITS/使用说明/QA/SHA256 清单（不含 RomFS PAK 和 ZIP）

## 明确排除

- `pc汉化版/`
- `xci本体/`
- `升级档v1.0.7/`
- 原版/合并版 RomFS
- 官方语音、CG、音乐等 PAK
- 完整 `05_build` 二进制构建树
- 完整 `06_release` LayeredFS RomFS 与 ZIP
- `07_archive/old_releases`
- 私有密钥（`prod.keys`、`*.keys` 等）

## 发布版本记录

历史 fix8 完整基线发布包：

`汉化工作/06_release/CLANNAD_CHS_LayeredFS_v1.0.7_fix8.zip`

历史 fix8 ZIP SHA256：

`BB6CD0AC5555F9830B9B4FA2495F4F3E1AA752D4831044CA9144B642DB9AF286`

最终发布 QA：`total_bad = 0`。

## 本地复现

完整复现仍需要用户合法持有的本地游戏资源。最终工程依赖与复现顺序见：

`汉化工作/docs/05-工程目录与复现说明.md`

仓库不会保存或分发游戏本体、系统密钥、固件或完整官方资源。

## 2026-10-14：fix10 修复升级包

- 最新 Release：[v1.0.7-fix10](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)
- 版本：`CLANNAD_CHS_v1.0.7_fix10_jumpfix_UPGRADE_20261014.zip`，大小 214,483,509 字节；SHA-256：`C960EFA7E8CDE73840DEC2E349155F239662CEDB5DA9033E303EBB2E0136CC30`。
- 已检查 213 个剧情脚本，修复 170 个场景共 6,566 处绝对跳转引用；修复后 SCRIPT SHA256：`DC2AD2D10654226C8013E46C07B8C9D44BC5CEC147500AB684AD66C26016D5AD`。
- 此 ZIP **仅为 fix8 完整汉化之上的升级修复包**：包含 `SCRIPT.PAK`、`FONT.PAK` 与唯一的 fix9 ExeFS IPS；另外五个 UI/资源 PAK 必须由 fix8 完整安装提供。
- README 已更新卸载旧版/安装修复的步骤；其它详细说明参阅 `汉化工作/docs/06-fix10-升级卸载与排错.md`。
- 出于 GitHub 单文件大小限制，发布 ZIP 作为 Release **附件**，不会直接进入 Git 提交。
- 早期 fix8、fix9 记录保留用于历史追溯，不应作为最新稳定版。
