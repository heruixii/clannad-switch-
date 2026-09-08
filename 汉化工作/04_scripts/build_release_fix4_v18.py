from pathlib import Path
import shutil,hashlib,json,zipfile,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rel=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix4';zipf=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix4.zip'
if rel.exists():shutil.rmtree(rel)
if zipf.exists():zipf.unlink()
rom=rel/'atmosphere/contents/0100A3A00CC7E000/romfs';rom.mkdir(parents=True)
full='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000';pd=rel/'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix4';pd.mkdir(parents=True)
sources={
'SCRIPT.PAK':R/'05_build/script_package/SCRIPT.PAK.out','FONT.PAK':R/'05_build/font_package_fix2/FONT.PAK.out','SYSCG.PAK':R/'05_build/ui_packages_v1/SYSCG.PAK.out','PARTS.PAK':R/'05_build/ui_packages_fix4/PARTS.PAK.out','PARTS2.PAK':R/'05_build/parts2_fix4/PARTS2.PAK.out','MANUAL.PAK':R/'05_build/ui_packages_v1/MANUAL.PAK.out','OTHCG.PAK':R/'05_build/OTHCG.PAK.out'}
for n,s in sources.items():shutil.copy2(s,rom/n)
shutil.copy2(R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips',pd/(full+'.ips'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest().upper()
readme=f'''CLANNAD Nintendo Switch 简体中文补丁 fix4\n\n适用：CLANNAD v1.0.7\nTitle ID：0100A3A00CC7E000\n程序 Module ID：{full}\n\nfix4 目的：修复 fix3 已全部汉化后仍出现的中英文重叠、中文互相重叠。\n\n本版改动\n========\n1. 设置页静态双层去重\n- 原版 CONFIG_BG_EN 与 CONFIG_TAB_EN 本来都带同一套页签，游戏通过层偏移使两套英文精准重合。\n- fix3 重画中文时，两层源图的 Y 几何关系被改坏，造成中文双影。\n- fix4 按原版实测关系恢复约 14px 的源图层间基线差，并让两层使用同一份中文字形像素。\n- 离线对齐后页签像素掩码 IOU=0.978（剩余差异为 CZ 调色板边缘量化）。\n\n2. 清理旧 PARTS 设置文字层\n- v1.0.7 由 PARTS2 承担最终设置页静态文字。\n- PARTS 中 CONFIG_BG/CONFIG_BG_EN/CONFIG_TAB/CONFIG_TAB_EN 改为无文字底图，避免旧层与 PARTS2 再叠画。\n\n3. ExeFS 全引用去重\n- fix3 有部分较长中文使用新字符串地址，原英文字符串本身仍存在。\n- fix4 扫描全程序所有 ADRP+ADD 引用并统一重定向，不再只修改 ConfigWin 主函数。\n- 已补出 English、Quick Load、Close、Defaults 等此前遗漏的第二引用。\n- QA：旧设置英文活跃引用组剩余 0；旧系统英文活跃引用组剩余 0；181 个配置引用点可见字符串校验错误 0。\n\n4. 未改动项目\n- 剧情 SCRIPT 不变。\n- 字体继续使用 fix2/fix3 已验证版本；缺字 0、Y 偏移 0。\n- 标题菜单不再次修改。标题两状态中文字形几何已验证为逐像素一致（偏移 817px 后 IOU=1.0），旧标题英文 OCR 命中 0。\n\n最终 QA\n=======\nSCRIPT/FONT/SYSCG/PARTS/PARTS2/MANUAL/OTHCG 全部结构及内容校验 bad=0。\n综合 TOTAL_BAD=0。\n设置静态英文 OCR 命中=0。\n\n安装\n====\n1. 建议删除旧 fix1/fix2/fix3 的 CLANNAD romfs 替换目录。\n2. 删除旧的 CLANNAD exefs_patches，避免多个 IPS 同时加载。\n3. 将本包内 atmosphere 复制到 SD 卡根目录。\n4. 必须使用 v1.0.7；其它版本 Module ID 不匹配。\n\n建议实机重点验证\n================\n- 设置页顶部 9 个页签是否只剩一份清晰中文。\n- 设置页 Language/Quick Load/Close/Defaults 等是否不再压着英文。\n- 设置正文及右侧说明是否不再出现中文双影。\n- 开始界面保持 fix3 的完整汉化状态。\n'''
(rel/'README.txt').write_text(readme,encoding='utf-8-sig')
qa=json.loads((R/'05_build/final_release_sources_verify_fix4.json').read_text(encoding='utf-8'));ipsqa=json.loads((R/'05_build/fix4_exefs/FINAL_IPS_QA_fix4.json').read_text(encoding='utf-8'));cqa=json.loads((R/'05_build/config_fix4_static_qa.json').read_text(encoding='utf-8'))
summary={'release':'fix4','target_version':'v1.0.7','module_id':full,'source_total_bad':qa['TOTAL_BAD'],'ips':ipsqa,'config_static':{'english_bad':len(cqa['english_bad']),'tab_layer_iou':cqa['tab_layer_iou_after_14px'],'tab_layer_xor':cqa['tab_layer_xor']}}
(rel/'FINAL_QA_SUMMARY_fix4.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
# sums
entries=[]
for f in sorted(rel.rglob('*')):
 if f.is_file() and f.name!='SHA256SUMS.txt':entries.append((sha(f),f.relative_to(rel).as_posix(),f.stat().st_size))
(rel/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {n}  ({s} bytes)' for h,n,s in entries)+'\n',encoding='utf-8')
# zip
with zipfile.ZipFile(zipf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for f in sorted(rel.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(rel).as_posix())
print('RELEASE',rel);print('ZIP',zipf,zipf.stat().st_size,sha(zipf));
for h,n,s in entries:print(h,s,n)
