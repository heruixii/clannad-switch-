# CLANNAD Switch 汉化项目基线与 PC 日中对齐

## 1. 项目目标

将 PC 版 CLANNAD Full Voice 的既有中文汉化安全移植到 Nintendo Switch 版 CLANNAD。优先复用既有译文，不做大规模润色；任何结构不确定的文本进入 review，不为追求覆盖率强行串行。

## 2. Switch 基线

- Base Title ID: `0100A3A00CC7E000`
- Base XCI: `xci本体/CLANNAD [JPN][0100A3A00CC7E000].xci`
- Update Title ID: `0100A3A00CC7E800`
- Update version: `1.0.7`
- Update source: `升级档v1.0.7/CLANNAD [US] [1.0.7].nsz`
- Update ticket: `0100a3a00cc7e8000000000000000008.tik`
- v1.0.7 Program NCA: `4c912979ef9a08f69f2008108c45ff26.nca`

`[US]` 只是升级档来源标签；ticket 已确认它属于同一 Title ID 系列，可作为 `0100A3A00CC7E000` 的更新基线。

当前执行环境允许读取/拆分 XCI/NSP/NSZ 容器，但不允许使用外部密钥解密 NCA 内容，因此尚未取得 Switch RomFS。未绕过该限制。

## 3. PC 脚本基线

PC 日文原版与 PC 中文汉化均使用 RealLive `SEEN.TXT`：

- archive index: 前 `10000 × 8 = 80000` 字节，为 `(offset, length)` 表
- JP 场景数: `231`
- ZH 场景数: `231`
- 场景编号集合: 完全一致

目录：

- `03_text/pc_jp/raw/SEEN####.TXT`
- `03_text/pc_zh/raw/SEEN####.TXT`

RealLive RLCMP 解压器：

- `04_scripts/decompress_reallive.py`
- compiler version: `110002`
- fixed 256-byte XOR + compiler 110002 second XOR + LZSS
- back-reference distance 正确公式：`count >> 4`

全量解压 QA：

- JP: `231/231`
- ZH: `231/231`
- errors: `0`

## 4. PC 文本结构

CLANNAD FV 正文文本点可由 RealLive 控制序列识别：

`0A <kidoku:u16> 40 <text_id:u16> <text...>`

绝对 `text_id` 和 `kidoku_id` 在不同编译版本间都会随增删/分支漂移，因此不能直接作为跨版本全局键。

最终采用：

1. 从严格正文 marker 提取 JP/ZH 文本事件；
2. 取相邻文本间 RealLive 控制块；
3. 将易漂移的 `0A/40` UInt16 operands 归零；
4. 对控制块做指纹；
5. 仅选择 JP/ZH 两边都唯一出现的控制指纹；
6. 对这些唯一指纹做单调 LIS，形成稳定结构锚链；
7. 两个连续锚之间若 JP/ZH 文本事件数相等，按位置映射；
8. 数量不等的局部区段全部进入 review，不猜测。

核心脚本：

- `04_scripts/extract_reallive_anchored_text.py`
- `04_scripts/analyze_control_fingerprints.py`
- `04_scripts/align_by_control_anchors.py`
- `04_scripts/build_pc_control_corpus.py`

## 5. 正式 PC 日中语料 v1

输出：

`03_text/matched/pc_control_parallel_v1/`

包含：

- 每场 `SEEN####.tsv`
- `all.tsv`
- `summary.tsv`

最终状态：

- JP 正文事件: `98,955`
- ZH 正文事件: `99,410`
- 安全映射: `90,793`
  - `anchor`: `16,998`
  - `equal-segment`: `73,795`
- JP 安全覆盖率: `91.752%`
- `review-jp`: `8,155`
- `review-zh`: `8,607`
- `review-type-mismatch`: `4`
- `review-decode-garbage`: `3`


安全集 QA：

- duplicate JP mapping: `0`
- duplicate ZH mapping: `0`
- non-monotonic scenes: `0`
- safe rows containing known decode-garbage markers: `0`
- dialogue/narration type mismatch in safe set: `0`

因此后续 Switch 自动移植只能消费 `anchor` 与 `equal-segment` 两类行；其余状态均不可自动回写。

## 6. PC 中文异常

### SEEN3419

`SEEN.TXT` archive 内的 3419 正文真实字节大量为 `0xCC` 占位，并非解码器错误；但 PC 汉化目录根部另有独立场景补丁：

`pc汉化版/CLANNAD/【key】clannad fv/seen3419.txt`

该文件是同场 RealLive 二进制，header 与 3419 对应，解压后中文正文完整。已非破坏性复制为：

`03_text/pc_zh/recovered/SEEN3419.TXT`

SHA256：`F10DA46122FD8AD9B2DFB05C96EF6AD672B052CDC4C40B6113BCAD6F1AF6BEDD`

对齐代码会优先使用 recovered 文件；原 `03_text/pc_zh/raw/SEEN3419.TXT` 保留不动。恢复结果：`185/185` 文本事件全部落入安全结构区。

### RLdev metadata

中文脚本中：

- 204 场带 RLdev metadata，`text_transform = None`
- 26 场无 RLdev metadata
- 只有 `SEEN9035` 标记 `text_transform = Chinese`

`SEEN9035` 当前严格正文 marker 未提取到实际正文，因此暂不影响主语料。

## 7. LucaSystemTools

Switch 版 CLANNAD 使用 Prototype LucaSystem。

工具：

`tools/LucaSystemTools`

固定源码 commit：

`d84738a787619b77d5b8e49007b16ddbc0c6a74b`

内置 CLANNAD opcode：

`LucaSystemTools/LucaSystemTools/LucaSystemTools/OPCODE/CL.txt`

源码原 target 为已退役 `netcoreapp3.1`。项目副本已最小迁移到 `net8.0`，只增加 `SYSLIB0011` 兼容 NoWarn，不改脚本解析逻辑。

当前 build：

- errors: `0`
- executable: `tools/LucaSystemTools/LucaSystemTools/LucaSystemTools/bin/Release/net8.0/LucaSystemTools.exe`

CL opcode 已包含 `TALKNAME_SET`, `MESSAGE`, `VOICE` 等。

## 8. Switch 侧预期路线

Switch 官方版同时支持日文与英文。取得 RomFS 后优先检查 Luca 脚本的语言存储方式：

1. 批量导出 CL 脚本 JSON / string text；
2. 识别 JP/EN 是否为并列槽、分离资源或运行时条件分支；
3. 若结构允许，优先保留日文槽并将英文槽替换为中文，以降低覆盖原日文结构的风险；
4. 用 Switch 日文文本与 `pc_control_parallel_v1` 的 JP 文本做场景级/序列级对齐；
5. 高置信映射搬 PC 中文；剩余 review 区使用日文/官方英文补译或人工确认；
6. 最后处理字体、标题/系统菜单、语言选择、Dangopedia/数字手册相关 UI。

## 9. 当前硬阻塞

当前唯一外部阻塞是 **Switch RomFS 尚不可读取**。工程已准备 LucaSystem CL 导入/导出工具与 90,793 条安全 PC 日中映射；一旦 `02_romfs/base` / `02_romfs/update` 获得已解包内容，即可直接进入 Switch 脚本扫描与对齐，无需重新处理 PC 侧。



## 10. PC 日中安全语料 v4（2026-09-07）

在 v1 的控制锚基础上继续进行了四层保守扩展：

1. `SEEN3419` 从 PC 汉化目录独立补丁 `seen3419.txt` 恢复，185/185 文本事件进入安全区；
2. 90 个唯一单条增删 review 块通过结构 QA，新增 `unique-gap` 495 对；
3. 15 个 margin 块逐块人工核对，13 块整体确认，`SEEN1516` / `SEEN6502` 只收前后明确对应部分，新增 `confirmed-gap` 81 对；
4. 递归局部控制锚仅接受 `same control fingerprint + same event index` 的硬条件候选，新增 `recursive-hard` 39 对。

当前正式安全语料：

`03_text/matched/pc_control_parallel_v4/all.tsv`

统计：

- JP 正文事件：`98,955`
- 安全映射：`91,412`
- 安全覆盖率：`92.377%`
- `anchor`: `16,998`
- `equal-segment`: `73,798`
- `name-event`: `1`
- `unique-gap`: `495`
- `confirmed-gap`: `81`
- `recursive-hard`: `39`
- remaining `review-jp`: `7,540`
- remaining `review-zh`: `7,992`
- remaining `review-type-mismatch`: `3`

安全集 QA：

- duplicate JP key: `0`
- duplicate ZH key: `0`
- known decode-garbage: `0`

剩余 review 多为 PC 汉化真实发生拆句、并句、漏句或改写的区段。后续不再为了提高 PC 对齐百分比强行配对；实际 Switch 对齐时，只有 Switch 真正命中这些区段才做局部复核/补译。

## 11. PC UI 汉化资产差分

已对 `clfvbak` 原版备份与汉化版做逐文件 SHA256 对比：

`03_text/pc_ui/pc-vs-backup-files.tsv`

共有 `155` 个同路径文件发生变化：

- `153` 个 `.g00`
- `1` 个 `GAMEEXE.INI`
- `1` 个 `SEEN.TXT`

其中 G00 包含配置菜单、保存读取、场景/音乐鉴赏、角色名、图文说明等大量已汉化 UI，可在 Switch RomFS 可读后作为 UI 术语与布局参考。

`GAMEEXE.INI` 的汉化适配还包含正文/名字字号、字符间距、每行字数、名字显示模式和选项字号等调整，可作为 Switch 字体与排版参数的经验基线。
