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

## 最终发布版本记录

最终本地发布包：

`汉化工作/06_release/CLANNAD_CHS_LayeredFS_v1.0.7_fix8.zip`

最终 ZIP SHA256：

`BB6CD0AC5555F9830B9B4FA2495F4F3E1AA752D4831044CA9144B642DB9AF286`

最终发布 QA：`total_bad = 0`。

## 本地复现

完整复现仍需要用户合法持有的本地游戏资源。最终工程依赖与复现顺序见：

`汉化工作/docs/05-工程目录与复现说明.md`

仓库不会保存或分发游戏本体、系统密钥、固件或完整官方资源。
