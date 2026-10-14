# fix10：全局剧情跳转修复与 QA 记录

目标：CLANNAD Switch v1.0.7，Title ID `0100A3A00CC7E000`。维护：ALTIRKIE。

## 崩溃根因与 A/B 过程

旧 No.1 存档在春原宿舍录音机桥段触发 `MakeTextThread` 用户异常。实机交叉对照：关闭 ExeFS 后仍崩溃；停用汉化 SCRIPT.PAK 后不再崩溃；关闭汉化字体但恢复 SCRIPT 后仍崩溃；只将 `SEEN0414` 全部中文正文改为同长度 ASCII 时仍崩溃。

从 `SEEN0414` 的 1729 条指令中追踪到 18 个 GOTO、13 个 IFN 和 4 个 ONGOTO 的**绝对跳转目标仍为原本英文字段长度下的旧位置**。如旧 `0xD1EC` 正确新目标为 `0x8FF6`，跳转越界；修正这 35 个引用并实机验证后闪退消失。

## 全局指针重定位

- 读取 230 个 PAK 条目，连续解析其中 213 个剧情脚本：目录越界或指令边界错误为 0。
- 重建旧绝对偏移与新指令的对应关系，扫描 GOTO、IFN、ONGOTO 以及 JUMP/FARCALL 的跨场景资源引用；**170 个场景共修复 6,566 个目标引用，实改 14,932 字节**。
- 修复不仅覆盖跳到文件末尾以外的指针，也覆盖**旧偏移恰好落在新脚本中另一个合法指令起点**的情况，避免错误的剧情分支。
- 所有修正后目标均由同一目标场景原指令索引映射到新偏移；没有需要解析但无法找到原始目标的引用。
- 不改变中文正文、不添加脚本条目、不改字体与 UI。修复文件大小仍为 15,867,120 字节。
- 重新运行可发布的 [rebase_script_absolute_branches_fix10.py](../04_scripts/rebase_script_absolute_branches_fix10.py)，从备份输入重建后**输出与实机部署的 fix10 SCRIPT.PAK 字节完全一致**；SHA-256 `DC2AD2D10654226C8013E46C07B8C9D44BC5CEC147500AB684AD66C26016D5AD`。

## ExeFS 与资源核对

fix10 升级包沿用经过用户测试的 fix9 ExeFS IPS，不更改字节。实机扫描确认仅一个对应 Build ID `CF38595316BAA425E792CE5CD122DFC6` 的有效 IPS，fix3～fix8 均停用。字体 `FONT.PAK` 已启用且用户确认中文正常。其它五个 PAK 保留原有完整 fix8 安装。

本地 fix10 ZIP：214,483,509 字节，所有档案成员 CRC 和 SHA-256 校验通过；ZIP SHA-256 `C960EFA7E8CDE73840DEC2E349155F239662CEDB5DA9033E303EBB2E0136CC30`。本地备份及 SD 读回已对 SCRIPT/IPS 进行哈希比对。

## 已知限制与后续 QA

这次已经完成旧存档原闪退点、后续日期、中文字体、设置界面、主角姓名和标题 UI 的实机验收。**并没有对全部角色、每条分支、团子百科每条词条或 After Story 全过程做穷尽式验证**；也没有在多个不同固件、游戏版本和不同旧存档上重复测试。若其他剧情节点出现新崩溃，应保存报告并单独定位。

## 复现命令（需用户自行合法拥有被汉化的 SCRIPT.PAK）

```bash
python 汉化工作/04_scripts/rebase_script_absolute_branches_fix10.py \
  --script /path/to/original-translated-SCRIPT.PAK \
  --messages 汉化工作/03_text/translated/message_targets_complete_v12.tsv \
  --selects 汉化工作/03_text/translated/select_targets_complete_v2.tsv \
  --output /path/to/empty-output-directory
```

只有原 SHA256 `42FD1C6865A1EB094542A0DC8E7E367B624FDCE6FDEDBF9E3E04D200B49DA767` 的输入文件才会通过默认防误用检查。写入前应备份所有旧文件，绝不直接覆盖输入。

## 2026-10-14：最终发布为完整单包（取代旧升级 ZIP）

从已存档 GitHub fix8 完整基础 ZIP 逐项提取另外五个原有汉化 PAK，确认 SHA-256 与工程发布校验文件一致；加上本次已通过实机验收的 `SCRIPT.PAK`、`FONT.PAK` 和唯一 fix9 ExeFS IPS，共七个 PAK 与一个 IPS。

**当前最终发布**：`CLANNAD_CHS_v1.0.7_fix10_FULL_20261014.zip`，大小 485,507,985 字节，SHA-256：`E8CC4767AB446CA2C9D550F3B1EECE91ACCF872549BF516EC69A6C43C04E4732`。发布 ZIP 全部 13 个成员经重新打开并逐个哈希验证；无需用户另外下载 fix8。

旧的 `CLANNAD_CHS_v1.0.7_fix10_jumpfix_UPGRADE_20261014.zip` 为临时升级版，不再作为最新公开下载提供。
