from pathlib import Path
import shutil,hashlib,json,zipfile
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rel=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix7';zipf=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix7.zip'
if rel.exists():shutil.rmtree(rel)
if zipf.exists():zipf.unlink()
rom=rel/'atmosphere/contents/0100A3A00CC7E000/romfs';rom.mkdir(parents=True)
full='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000';pd=rel/'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix7';pd.mkdir(parents=True)
sources={
'SCRIPT.PAK':R/'05_build/script_package_fix7/SCRIPT.PAK.out',
'FONT.PAK':R/'05_build/font_package_fix2/FONT.PAK.out',
'SYSCG.PAK':R/'05_build/ui_packages_v1/SYSCG.PAK.out',
'PARTS.PAK':R/'05_build/ui_packages_fix5/PARTS.PAK.out',
'PARTS2.PAK':R/'05_build/parts2_fix4/PARTS2.PAK.out',
'MANUAL.PAK':R/'05_build/ui_packages_v1/MANUAL.PAK.out',
'OTHCG.PAK':R/'05_build/OTHCG.PAK.out'}
for n,s in sources.items():shutil.copy2(s,rom/n)
shutil.copy2(R/'05_build/fix7_exefs/CF38595316BAA425E792CE5CD122DFC6.ips',pd/(full+'.ips'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest().upper()
readme=f'''CLANNAD Nintendo Switch 简体中文补丁 fix7

适用：CLANNAD v1.0.7
Title ID：0100A3A00CC7E000
程序 Module ID：{full}

fix7 重点修复
============
1. 主角默认名英文修复
- 正式剧情 SEEN2417 中存在“朋也 / Tomoya”双语言槽；游戏保持 English UI 状态时会选择 Tomoya。
- fix7 将正式流程英文槽原位替换为“朋也”，Tomoya 剩余 0。
- 姓名设置中的两条 Okazaki Tomoya 英文语音提示也原位改为中文。
- 不修改 Z_TEST 测试脚本，不改变语言状态和配音判定逻辑。

2. 继续完整继承 fix6
- 游戏内剩余按钮中英文重叠
- 在实际应用 fix5/fix4 IPS 后重新扫描程序，确认仍活跃的短按钮英文为 Yes / No / Back / Next。
- Yes → 官方简中“是”；No → 官方简中“否”；Back → 官方简中“返回”。
- Next 原版其它语言槽为空，因此在已验证字符串池安全尾部新增“下一项”，并把 3 个实际调用点全部重定向。
- 补丁后 Yes/No/Back/Next 旧英文活跃引用总数 = 0。
- 继续沿用 fix5 对 SKIP_ICON_00/01 静态 Skip/Back/Jump 英文的清除，以及 SELECT → 选择。

- 团子百科底部目录挤在一起
- 找到真正原因：_KEYWORD 的第 1 字段不是玩家显示标题，而是目录排序/分组键。
- 游戏会按这个字段的首字母分组，并且同一字母每组最多 6 项；英文原版因此形成 A/B/C...目录。
- fix5 把内部排序键也翻成中文，导致 71 个词条按不同汉字首字分成大量目录组，全部挤在底部。
- fix7 恢复第 1 字段为原版英文内部排序键；彩色可见标题、正文A、正文B继续保持完整简中。
- 目录恢复为 22 个原生字母组；可见英文正文/标题残留 = 0。
- “There are no keywords.” 也改为“没有百科词条。”。

- 沿用此前稳定修复
- fix5：按钮静态 Skip/Back/Jump 清理、SELECT 汉化、团子百科 71 条正文汉化。
- fix4：设置页双层几何修正、动态 UI 全引用去重。
- fix3/fix2：标题菜单、字体、系统 UI 等既有修复。

最终 QA
=======
- 7 个 PAK：SCRIPT / FONT / SYSCG / PARTS / PARTS2 / MANUAL / OTHCG 全部 bad=0。
- 团子百科：71 条，parse bad=0，可见英文残留=0，内部排序键恢复，目录组数=22。
- 静态按钮英文残留=0。
- 动态按钮旧英文引用=0，按钮目标解析错误=0。
- 字体缺字=0。
- 设置静态英文残留=0，层对齐 IOU=0.978。
- 综合 TOTAL_BAD=0。

安装
====
1. 删除或移走旧 fix1～fix5 的 CLANNAD romfs 替换目录。
2. 删除旧 CLANNAD exefs_patches，尤其不要让 fix5 和 fix7 IPS 同时加载。
3. 将本包内 atmosphere 文件夹复制到 SD 卡根目录。
4. 必须使用 CLANNAD v1.0.7。

实机重点验证
============
- Yes/No/Back/Next 类按钮是否只显示一份中文。
- 快进/回退/跳转等按钮是否继续保持 fix5 的无英文状态。
- 团子百科底部目录是否恢复清晰的 A/B/C...字母分组。
- 打开百科条目后，彩色标题与正文是否仍为中文。
'''
(rel/'README.txt').write_text(readme,encoding='utf-8-sig')
qa=json.loads((R/'05_build/final_release_sources_verify_fix7.json').read_text(encoding='utf-8'));iq=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8'));kq=json.loads((R/'05_build/keyword_fix6/keyword_fix6_qa.json').read_text(encoding='utf-8'))
summary={'release':'fix7','target_version':'v1.0.7','module_id':full,'source_total_bad':qa['TOTAL_BAD'],'name_qa':iq,'keyword':kq}
(rel/'FINAL_QA_SUMMARY_fix7.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
entries=[]
for f in sorted(rel.rglob('*')):
 if f.is_file() and f.name!='SHA256SUMS.txt':entries.append((sha(f),f.relative_to(rel).as_posix(),f.stat().st_size))
(rel/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {n}  ({s} bytes)' for h,n,s in entries)+'\n',encoding='utf-8')
with zipfile.ZipFile(zipf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for f in sorted(rel.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(rel).as_posix())
print('RELEASE',rel);print('ZIP',zipf,zipf.stat().st_size,sha(zipf))
for h,n,s in entries:print(h,s,n)
