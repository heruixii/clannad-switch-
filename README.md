# CLANNAD Nintendo Switch 简体中文移植工程

这是《CLANNAD》Nintendo Switch v1.0.7 简体中文移植工程的源码级备份。

- Switch 移植汉化：**ALTIRKIE**
- PC 中文译文来源：**CLANNAD FV 汉化补丁 2.0**
- 目标版本：Nintendo Switch《CLANNAD》v1.0.7
- Title ID：`0100A3A00CC7E000`
- 最终实机版本：`fix8`

## 汉化范围

包含本篇、各角色路线、**After Story（后日谈）**、剧情选项、系统 UI、设置、团子百科、主角姓名逻辑及相关手册/UI 适配。

## 仓库内容

本仓库用于备份汉化工程本身，不包含完整游戏本体或官方资源。主要保留：

- 构建/转换/QA 脚本；
- 最终译文目标表与文本工作结果；
- 团子百科翻译数据；
- fix8 ExeFS IPS 与 QA 元数据；
- 贡献、安装、复现文档；
- 问题定位/分析脚本归档。

完整游戏 XCI、PC 游戏文件、NSZ/NCA、原版 RomFS、官方 PAK、完整 LayeredFS 发布包以及旧版本发布包不会提交到 GitHub。

详细说明见：

- `汉化工作/docs/03-贡献与署名.md`
- `汉化工作/docs/04-最终用户使用说明.md`
- `汉化工作/docs/05-工程目录与复现说明.md`
- `GITHUB_BACKUP.md`

## fix9-test：通关系统数据确认闪退热修复

fix8 已收到一项真机问题报告：完成路线后出现“过关信息（系统文件）已保存”提示时，按 A 确认可能直接闪退。

离线回溯定位到 fix4 开始引入的 `Close` 全引用重定向：历史 fix3 只修改 1 处显示引用，fix4 为消除英文残留又将另外 6 处程序引用统一重定向到中文字符串。fix9-test 保留显示用中文引用，仅撤销这 6 组后加的全局引用。

离线差分验证：

- 相对 fix8 仅移除 48 个 IPS 补丁字节；
- 未新增或修改其它 fix8 补丁字节；
- `Close` 中文目标从 7 处重定向恢复为仅 1 处显示引用；
- fix8 的姓名运行时修复 7 个代码点全部保持不变；
- IPS 结构无重叠，QA `total_bad = 0`。

当前 `v1.0.7-fix9-test` 仍为 **真机验证候选**。已经安装 fix8 的用户只需替换 ExeFS IPS，不需要重新下载或替换 RomFS PAK。安装时必须先删除旧的 `atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix8/`，不要让 fix8 与 fix9 两套 IPS 同时生效。
