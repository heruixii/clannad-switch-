# CLANNAD Switch RomFS 接入与后续流水线

## 当前状态

Switch Base/Update 容器和 Title ID 已验证，但当前执行环境不能使用外部密钥解密 NCA；因此 `02_romfs/base` 与 `02_romfs/update` 目前为空。

这不是脚本或翻译工具故障。PC 日中语料、LucaSystemTools 和自动接入脚本均已准备完成。

## 需要的输入目录

已解包的可读 RomFS 内容应放入：

- `02_romfs/base/`
- `02_romfs/update/`（v1.0.7；若只拿到已合并后的最终 RomFS，也可先放在 base，update 留空）

不要把 XCI/NSZ/NCA 文件直接放进这两个目录；这里需要的是 RomFS 内真实文件树。

## 一键接入

脚本：

`04_scripts/prepare_switch_pipeline.py`

功能：

1. 将 base 与 update overlay 合并为 `02_romfs/merged-v1.0.7/`；
2. 统计扩展名和资源分布；
3. 将 `.pak` 复制到 `03_text/switch_work/paks/` 后解包，避免污染原 RomFS；
4. 搜索 `.scr`；
5. 使用 net8 版 LucaSystemTools + `CL.txt` opcode 导出 JSON；
6. 同时用 `OnlyText=translate` 导出带稳定 code/param index 的文本；
7. 汇总到 `03_text/switch_extracted/all_strings.tsv`。

当前空目录 dry-run 结果按设计返回：

`status = blocked-no-romfs`

不会在没有 RomFS 的情况下生成伪结果。

## LucaSystemTools

源码：`tools/LucaSystemTools`

固定 commit：`d84738a787619b77d5b8e49007b16ddbc0c6a74b`

项目副本已从退役 `netcoreapp3.1` 最小迁移到 `net8.0`，CLI 自检：

- CLANNAD (`CL`) 在 supported game list 中
- build errors: `0`
- `LucaSystemTools.exe -l` exit code: `0`

## RomFS 到位后的执行顺序

1. 跑 `prepare_switch_pipeline.py`；
2. 确认 Switch 脚本数量、JP/EN 存储结构；
3. 优先保留 JP 槽，若结构允许，将官方 EN 槽替换为中文；
4. 用 Switch JP 对齐 `pc_control_parallel_v4` 的 JP 侧；
5. 安全命中直接搬 PC 中文；
6. 未命中/PC review/主机独占文本使用 Switch JP + 官方 EN 局部补译；
7. 回写 Luca 脚本并重新导出复核；
8. 处理字体覆盖；
9. 处理 UI / Dangopedia / 数字手册 / 语言选择等资源；
10. LayeredFS 组包；
11. 全量重提取、控制码、字体和文件继承 QA；
12. 随机文本抽检后出最终测试包。

## 不会做的事情

- 不从加密 NCA 猜脚本内容；
- 不为追求 PC 对齐百分比强制配对剩余 review；
- 不覆盖或删除原始 XCI / NSZ / PC 汉化备份；
- 不把开发工具或密钥文件打进发布补丁。
