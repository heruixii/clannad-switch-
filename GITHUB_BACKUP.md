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

## 历史发布归档记录

历史 fix8 完整基线发布包：

`汉化工作/06_release/CLANNAD_CHS_LayeredFS_v1.0.7_fix8.zip`

历史 fix8 ZIP SHA256：

`BB6CD0AC5555F9830B9B4FA2495F4F3E1AA752D4831044CA9144B642DB9AF286`

最终发布 QA：`total_bad = 0`。

## 本地复现

完整复现仍需要用户合法持有的本地游戏资源。最终工程依赖与复现顺序见：

`汉化工作/docs/05-工程目录与复现说明.md`

仓库不会保存或分发游戏本体、系统密钥、固件或完整官方资源。


## 当前发布：fix10 完整安装包（2026-10-14）

当前唯一推荐从 GitHub Release 下载的版本：`v1.0.7-fix10`，附件 `CLANNAD_CHS_v1.0.7_fix10_FULL_20261014.zip`，大小 485,507,985 字节，SHA-256：`E8CC4767AB446CA2C9D550F3B1EECE91ACCF872549BF516EC69A6C43C04E4732`。

完整包包含七个 RomFS PAK + 一个 fix9 ExeFS IPS，**无需再安装 fix8/fix9**。此前发布的 fix10 升级包为临时中间产物，已被完整包取代。

安装、卸载、清理旧版本请参阅 `汉化工作/docs/06-fix10-升级卸载与排错.md`。fix8/fix9 的二进制备份仍保留在本地诊断目录用于追溯，GitHub 仓库继续只提交文本、脚本和 QA，不向 Git 历史直接添加约 463 MiB 的 ZIP。
