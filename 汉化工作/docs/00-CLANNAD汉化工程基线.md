# CLANNAD Nintendo Switch 中文化工程基线

## 1. 目标版本

- Base Title ID: `0100A3A00CC7E000`
- Update Title ID: `0100A3A00CC7E800`
- 当前更新基线: `v1.0.7`
- 本体素材: `D:\switch游戏\个人汉化\clannad\xci本体\CLANNAD [JPN][0100A3A00CC7E000].xci`
- 更新素材: `D:\switch游戏\个人汉化\clannad\升级档v1.0.7\CLANNAD [US] [1.0.7].nsz`

更新包 ticket 为 `0100a3a00cc7e8000000000000000008.tik`，因此文件名中的 `[US]` 不是另一套 Title ID；它属于上述 Base 的 Update 链。

## 2. PC 汉化源

- PC 中文版 `SEEN.TXT`:
  `D:\switch游戏\个人汉化\clannad\pc汉化版\CLANNAD\【key】clannad fv\SEEN.TXT`
  - size: 7,171,753 bytes
- PC 原日文备份 `SEEN.TXT`:
  `D:\switch游戏\个人汉化\clannad\pc汉化版\CLANNAD\【key】clannad fv\clfvbak\SEEN.TXT`
  - size: 9,238,386 bytes

两份 archive 均拆出 **231 个非空场景**，场景编号集合完全一致。

## 3. RealLive / CLANNAD FV 解析状态

项目内最小工具：

- `04_scripts/split_seen.py`
- `04_scripts/decompress_reallive.py`
- `04_scripts/extract_text_islands.py`
- `04_scripts/align_pc_parallel.py`
- `04_scripts/build_pc_bilingual_map.py`

已验证：

- PC 日文 231/231 场 RLCMP 解压成功
- PC 中文 231/231 场 RLCMP 解压成功
- compiler version 为 `110002`
- 必须处理 CLANNAD FV 的第二层 XOR
- LZ back-reference 距离必须按 rldev 原实现化简为 `dst - (count >> 4)`，**不能额外 +1**

抽样已确认 `SEEN0414` 可得到：

- `この町は嫌いだ。` ↔ `我讨厌这座小镇。`
- `忘れたい思い出が染みついた場所だから。` ↔ `因为这里满是想要忘却的回忆。`

当前 PC 日中映射策略为保守单调 DP：

- 自动迁移只接受高置信 `1:1`
- 不同类别（旁白 / 对话 / 资源）不强配
- 不同说话人不强配
- 旁白与对话禁止 1↔2 合并
- 短语气句、喘息、纯省略号若旧 PC 汉化没有独立中文行，则保留为 review/缺口，禁止吞掉下一句中文
- 任何 `1:0 / 0:1 / 1:2 / 2:1` 一律不直接自动迁移

## 4. Switch LucaSystem 工具链

使用：`tools/LucaSystemTools`

固定 upstream commit:

`d84738a787619b77d5b8e49007b16ddbc0c6a74b`

仓库已自带 CLANNAD opcode：

`LucaSystemTools/LucaSystemTools/LucaSystemTools/OPCODE/CL.txt`

CLANNAD 关键 opcode 包括：

- `TALKNAME_SET`
- `MESSAGE`
- `MESSAGE_CLEAR`
- `MESSAGE_WAIT`
- `LOG`
- `VOICE`
- `SELECT`

原项目锁定 `netcoreapp3.1`，本机不存在 .NET Core 3.1 runtime/ref pack；项目副本已做**仅构建兼容**的最小迁移：

- TargetFramework: `net8.0`
- `SYSLIB0011` 仅关闭 obsolete 编译错误，以保持旧 `BinaryFormatter` 逻辑不变
- 不修改 CLANNAD 脚本解析/编译核心逻辑

当前可执行文件：

`tools/LucaSystemTools/LucaSystemTools/LucaSystemTools/bin/Release/net8.0/LucaSystemTools.exe`

SHA256:

`16818CA1462AF6FE9CBF7EEF1FD21C75FB6A0DCC1EEC746AB9437FEC16859F1E`

原 `.NET Core 3.1` 项目文件备份：

`LucaSystemTools.csproj.net31.bak`

## 5. rldev 参考实现

使用源码：`tools/rldev`

固定 commit:

`074c8b1aa81f3fe7ce71a36be3408082f3d4fc20`

用途：

- 校验 `SEEN.TXT` archive 结构
- 校验 RLCMP/XOR/LZ 算法
- 校验 RealLive `read_textout` 规则

本机未安装 OCaml/OMake，且仓库不含预编译 `kprl.exe`，因此当前不依赖构建 rldev；已把必要算法最小移植到 Python。

## 6. 当前 Switch 容器状态与边界

Base XCI Secure 分区已识别 4 个 NCA；最大 Program 内容约 5.76GB。

v1.0.7 更新 NSZ 已还原成 NSP 容器，并抽出：

- `4c912979ef9a08f69f2008108c45ff26.nca` — 42,359,296 bytes（Program update）
- `92ab09f7d27560b3f63f117176594716.cnmt.nca`
- `966756700c353df46f5b4087f777b527.nca`
- `ad9d83e6e649c37fd08471c162ddaa05.nca`
- ticket/cert

当前执行环境不允许通过外部密钥参数解密 NCA/RomFS；不绕过此限制。因此 Switch 脚本迁移阶段应以**已有合法解包 RomFS**为输入。一旦 RomFS 位于 `02_romfs`，LucaSystemTools 已经可直接进入脚本导出/对齐/回编译。

## 7. 后续顺序

1. 完成 231 场 PC 日中高置信映射和 review 队列。
2. 获取/发现可读取的 Switch v1.0.7 merged RomFS。
3. 用 LucaSystemTools `CL.txt` 识别所有脚本，导出 JSON/string。
4. 先做 Switch 日文 ↔ PC 日文对齐，再携带 PC 中文迁移，禁止直接按条数硬配。
5. 优先确认 Switch 内置 JP/EN 是否为双槽文本；若结构允许，优先保留 JP、以中文替换 EN 槽。
6. 处理字体覆盖、系统/UI、Dangopedia、语言选择、数字手册等非剧情文本。
7. 独立回读 QA 后才组装 LayeredFS 测试包。
