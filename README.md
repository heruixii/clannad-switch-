# CLANNAD Nintendo Switch 简体中文汉化（ALTIRKIE）

**当前版本：CLANNAD v1.0.7 fix10 · 完整一包安装版（2026-10-14）**

- 游戏：Nintendo Switch《CLANNAD》v1.0.7
- Title ID：`0100A3A00CC7E000`
- Nintendo Switch 移植汉化：**ALTIRKIE**
- PC 中文文本基础：**CLANNAD FV 汉化补丁 2.0**

## 下载——只需一个完整包

[**下载 fix10 完整汉化包（约 463 MiB）**](https://github.com/heruixii/clannad-switch-/releases/download/v1.0.7-fix10/CLANNAD_CHS_v1.0.7_fix10_FULL_20261014.zip) · [GitHub Release 与校验文件](https://github.com/heruixii/clannad-switch-/releases/tag/v1.0.7-fix10)

`CLANNAD_CHS_v1.0.7_fix10_FULL_20261014.zip`

**本版本已经整合旧 fix8 完整汉化资源与 fix10 剧情修复，首次安装无需再下载 fix8/fix9。** 只需一个 ZIP，内含全部七个 RomFS PAK 和一个 ExeFS IPS。老版本安装包已停止发布，避免用户误装、叠装。

## 新用户：直接安装

1. 确认游戏已经更新到 **v1.0.7**，通过 Atmosphère 正常启动。
2. 完全退出游戏，建议先备份 SD 卡与存档。
3. 下载 fix10 ZIP，解压后得到 `atmosphere` 文件夹，**将它复制到 SD 卡根目录并合并**。
4. 检查有七个 RomFS PAK，且对本游戏仅有**一个生效的** ExeFS IPS。启动游戏即可。

## 旧版用户：先清理，再直接安装

1. 退出 CLANNAD，**备份**旧汉化文件和游戏存档。
2. 仅从 SD 卡 `atmosphere/exefs_patches/` 移走 `CLANNAD_CHS_*` 旧目录（fix3～fix9 等）；**不要动其它游戏补丁**。
3. 从 SD 卡 `atmosphere/contents/0100A3A00CC7E000/romfs/` 移走旧汉化安装的七个 PAK 和已备份的 `.disabled` 调试副本。**不要删除游戏本体、存档或其它 Mod**。
4. 解压最新的 fix10 完整 ZIP，将其 `atmosphere` 放到 SD 卡根目录，合并文件夹。
5. 完全重启 CLANNAD，读取原存档，检查中文与剧情。

> **为什么内部 ExeFS 目录仍叫 `fix9`？** fix10 修正的是剧情 `SCRIPT.PAK` 的跳转地址，程序 IPS 沿用实机验证过的 fix9 二进制。不要额外启用任何历史 IPS。

查看 [详细安装、升级、完全卸载与排错指南](汉化工作/docs/06-fix10-升级卸载与排错.md)。

## 正确安装后的文件结构

```text
atmosphere/
├── contents/0100A3A00CC7E000/romfs/
│   ├── SCRIPT.PAK
│   ├── FONT.PAK
│   ├── MANUAL.PAK
│   ├── OTHCG.PAK
│   ├── PARTS.PAK
│   ├── PARTS2.PAK
│   └── SYSCG.PAK
└── exefs_patches/CLANNAD_CHS_v1.0.7_fix9/
    └── CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000.ips
```

## 修复结果与验收范围

之前使用 No.1 存档在春原宿舍录音机剧情处出现 `MakeTextThread` 崩溃。原因是重编译后的脚本仍保留原文本长度对应的旧绝对跳转地址。fix10 全局解析 **213 个脚本**，修正 **170 个场景、6,566 个跳转地址引用**，保留原有中文文本。

2026-10-14 已在实际 Switch 上确认原崩溃点及后续日期不再闪退、中文正常、标题菜单/设置/主角姓名正常。**尚未逐条完整通关全部角色路线和 After Story**，不承诺不存在任何未发现的新问题。

汉化涵盖本篇、各角色线、After Story、系统按钮与提示、菜单设置、团子百科、主角姓名和相关中文界面/手册。

详细技术信息：[修复根因与全局 QA](汉化工作/docs/07-fix10-根因与全局QA.md)。

## 校验

- 完整 ZIP 大小：**485,507,985 字节**（约 463 MiB）
- SHA-256：`E8CC4767AB446CA2C9D550F3B1EECE91ACCF872549BF516EC69A6C43C04E4732`
- 压缩包含完整 7 个 PAK + 1 个 IPS，所有内容已逐个 SHA-256 核对。

## 工程与贡献

仓库保留可复现的脚本处理流程和 QA 文档；[修复脚本](汉化工作/04_scripts/rebase_script_absolute_branches_fix10.py) 可在提供原始合法获取的汉化脚本和译文表后重建，结果与实机验证的 `SCRIPT.PAK` 字节相同。仓库 Git 提交不放入游戏本体或密钥。

原作 KEY / VisualArt's，PC 中文译文来源 CLANNAD FV 汉化补丁 2.0；未能核实的原汉化组成员姓名不自行补造。Switch 移植汉化：**ALTIRKIE**。更多见 [贡献与署名](汉化工作/docs/03-贡献与署名.md)。

### 问题反馈

如发现崩溃，请提供游戏版本、剧情日期、存档位置、截图和 Atmosphère 崩溃日志。不要通过反复覆盖原存档来测试。
