from pathlib import Path
import shutil,hashlib,json,zipfile
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rel=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix5';zipf=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix5.zip'
if rel.exists():shutil.rmtree(rel)
if zipf.exists():zipf.unlink()
rom=rel/'atmosphere/contents/0100A3A00CC7E000/romfs';rom.mkdir(parents=True)
full='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000';pd=rel/'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix5';pd.mkdir(parents=True)
sources={
'SCRIPT.PAK':R/'05_build/script_package_fix5/SCRIPT.PAK.out',
'FONT.PAK':R/'05_build/font_package_fix2/FONT.PAK.out',
'SYSCG.PAK':R/'05_build/ui_packages_v1/SYSCG.PAK.out',
'PARTS.PAK':R/'05_build/ui_packages_fix5/PARTS.PAK.out',
'PARTS2.PAK':R/'05_build/parts2_fix4/PARTS2.PAK.out',
'MANUAL.PAK':R/'05_build/ui_packages_v1/MANUAL.PAK.out',
'OTHCG.PAK':R/'05_build/OTHCG.PAK.out'}
for n,s in sources.items():shutil.copy2(s,rom/n)
shutil.copy2(R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips',pd/(full+'.ips'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest().upper()
readme=f'''CLANNAD Nintendo Switch 简体中文补丁 fix5\n\n适用：CLANNAD v1.0.7\nTitle ID：0100A3A00CC7E000\n程序 Module ID：{full}\n\nfix5 新增修复\n============\n1. 游戏内按钮中英文重叠\n- 定位到 Switch 专用 SKIP_ICON_00 / SKIP_ICON_01 中仍保留静态 Skip / Back / Jump 英文。\n- 这些按钮同时存在程序动态中文，因此 fix5 不再在贴图里画第二份中文，而是清除静态英文，只保留程序中文，避免中英或中文双层叠字。\n- PS_BUTTON_CHIP 中 START 已汉化，剩余纯贴图 SELECT 改为“选择”。\n- 按钮最终 OCR：Skip / Back / Jump / SELECT 英文命中 0。\n\n2. 团子百科正文完整汉化\n- 找到 SCRIPT.PAK 中之前漏掉的特殊条目 _KEYWORD。\n- fix4 的 _KEYWORD 与 Switch 原版逐字节相同，因此此前百科正文确实完全未汉化。\n- _KEYWORD 实际包含 71 个百科条目，每条为标题、彩色标题、正文A、正文B。\n- fix5 已完成 71/71 标题及正文简体中文翻译，并重新计算变长 UTF-16LE 记录长度。\n- 反向解析 71/71 成功，旧英文整段正文残留 0，新增字库缺字 0。\n\n沿用 fix4 修复\n============\n- 设置页静态双层几何恢复，层对齐 IOU=0.978。\n- PARTS 旧设置文字层中和，由 v1.0.7 PARTS2 负责最终静态页签。\n- ExeFS 全程序 UI 英文引用统一重定向，旧设置/系统英文活跃引用剩余 0。\n- 标题菜单、字体、剧情脚本主体继续沿用已验证版本。\n\n最终 QA\n=======\nSCRIPT/FONT/SYSCG/PARTS/PARTS2/MANUAL/OTHCG 全部 bad=0。\n团子百科：71 条，parse bad=0，英文正文残留=0，字体缺字=0。\n按钮英文残留=0。\n综合 TOTAL_BAD=0。\n\n安装\n====\n1. 删除或移走旧 fix1/fix2/fix3/fix4 的 CLANNAD romfs 替换目录。\n2. 删除旧的 CLANNAD exefs_patches，避免多个 IPS 同时加载。\n3. 将本包内 atmosphere 文件夹复制到 SD 卡根目录。\n4. 必须使用 v1.0.7；其它版本 Module ID 不匹配。\n\n建议真机重点验证\n================\n- 快进/回退/跳转等按钮是否只剩一份中文，不再压着英文。\n- START/SELECT 类提示是否正常。\n- 团子百科逐项打开，标题和正文是否均为中文、换行是否正常。\n- 设置页及系统弹窗保持 fix4 的去重状态。\n'''
(rel/'README.txt').write_text(readme,encoding='utf-8-sig')
qa=json.loads((R/'05_build/final_release_sources_verify_fix5.json').read_text(encoding='utf-8'));kq=json.loads((R/'05_build/keyword_fix5/keyword_fix5_qa.json').read_text(encoding='utf-8'));bq=json.loads((R/'05_build/button_fix5/button_fix5_ocr_qa.json').read_text(encoding='utf-8'))
summary={'release':'fix5','target_version':'v1.0.7','module_id':full,'source_total_bad':qa['TOTAL_BAD'],'keyword':kq,'button_english_bad':len(bq['bad']),'exefs_ips_sha256':sha(R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips')}
(rel/'FINAL_QA_SUMMARY_fix5.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
entries=[]
for f in sorted(rel.rglob('*')):
 if f.is_file() and f.name!='SHA256SUMS.txt':entries.append((sha(f),f.relative_to(rel).as_posix(),f.stat().st_size))
(rel/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {n}  ({s} bytes)' for h,n,s in entries)+'\n',encoding='utf-8')
with zipfile.ZipFile(zipf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for f in sorted(rel.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(rel).as_posix())
print('RELEASE',rel);print('ZIP',zipf,zipf.stat().st_size,sha(zipf))
for h,n,s in entries:print(h,s,n)
