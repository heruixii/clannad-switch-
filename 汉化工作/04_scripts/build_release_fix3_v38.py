from pathlib import Path
import shutil,hashlib,json,datetime
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
release=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix3'
if release.exists(): shutil.rmtree(release)
romfs=release/'atmosphere/contents/0100A3A00CC7E000/romfs';romfs.mkdir(parents=True)
patchdir=release/'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix3';patchdir.mkdir(parents=True)
full_module='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000'
sources={
 'SCRIPT.PAK':R/'05_build/script_package/SCRIPT.PAK.out',
 'FONT.PAK':R/'05_build/font_package_fix2/FONT.PAK.out',
 'SYSCG.PAK':R/'05_build/ui_packages_v1/SYSCG.PAK.out',
 'PARTS.PAK':R/'05_build/ui_packages_v1/PARTS.PAK.out',
 'PARTS2.PAK':R/'05_build/parts2_fix2/PARTS2.PAK.out',
 'MANUAL.PAK':R/'05_build/ui_packages_v1/MANUAL.PAK.out',
 'OTHCG.PAK':R/'05_build/OTHCG.PAK.out',
}
for name,src in sources.items():
    assert src.exists(),src
    shutil.copy2(src,romfs/name)
ips_src=R/'05_build/fix3_exefs/CF38595316BAA425E792CE5CD122DFC6.ips'
assert ips_src.exists()
ips_dst=patchdir/(full_module+'.ips');shutil.copy2(ips_src,ips_dst)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest().upper()
files=[]
for f in sorted(release.rglob('*')):
    if f.is_file():files.append({'path':f.relative_to(release).as_posix(),'size':f.stat().st_size,'sha256':sha(f)})
qa=json.loads((R/'05_build/final_release_sources_verify_fix3.json').read_text(encoding='utf-8'))
ipsqa=json.loads((R/'05_build/fix3_exefs/FINAL_IPS_QA_fix3.json').read_text(encoding='utf-8'))
summary={
 'release':'fix3','title_id':'0100A3A00CC7E000','update_title_id':'0100A3A00CC7E800','baseline':'v1.0.7',
 'main_module_id_full':full_module,'main_build_id_short':'CF38595316BAA425E792CE5CD122DFC6',
 'pak_verify_total_bad':qa['TOTAL_BAD'],'config_strings':ipsqa['config_strings'],'config_ref_sites':ipsqa['config_ref_sites'],
 'config_bad':ipsqa['config_bad'],'system_groups':ipsqa['system_groups'],'system_bad':ipsqa['system_bad'],
 'title_old_menu_hits':qa['AUX_QA']['title_old_menu_hits'],'font_report_failures':qa['AUX_QA']['font_report_failures'],
 'font_required_zh_missing':qa['AUX_QA']['font_required_zh_missing'],'font_y_min':qa['AUX_QA']['font_new_slot_y_min'],'font_y_max':qa['AUX_QA']['font_new_slot_y_max'],
 'files':files,
}
(release/'FINAL_QA_SUMMARY_fix3.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
readme=f'''CLANNAD Nintendo Switch 简体中文补丁 fix3\n\n适用游戏：CLANNAD Nintendo Switch\nTitle ID：0100A3A00CC7E000\n更新基线：v1.0.7\n程序 Module ID：{full_module}\n\n本版修复重点\n============\n1. 标题菜单中英文重叠\n   - fix2 只补了普通态 Alpha，RGB 中仍可能保留旧英文笔画。\n   - fix3 同时清理普通态 RGB + Alpha，再写入中文。\n   - TITLE 的 R/G/B/A/原始 RGB/黑底可见合成六种扫描中，9 个旧英文菜单词命中均为 0。\n\n2. 设置界面大量英文与中英文重叠\n   - 静态页签仍由 PARTS2.PAK 汉化。\n   - 另外新增 v1.0.7 专用 Atmosphere ExeFS IPS，将 ConfigWin 的英文动态 UI 槽替换/重定向为简体中文。\n   - 共覆盖 151 条设置 UI 文案、169 个代码引用点，离线回放错误 0。\n   - 另覆盖 36 组通用系统 UI（保存/读取/覆盖/删除/返回标题/跳转/恢复默认等），错误 0。\n\n3. 字体\n   - 使用 fix2 的分字体家族补字版本。\n   - 3497 个所需中文缺字 0；新增字槽 Y 偏移 min=0 / max=0；字体 QA 失败 0。\n\n最终离线 QA\n============\n- SCRIPT.PAK：bad 0\n- FONT.PAK：bad 0\n- SYSCG.PAK：bad 0\n- PARTS.PAK：bad 0\n- PARTS2.PAK：bad 0\n- MANUAL.PAK：bad 0\n- OTHCG.PAK：bad 0\n- 综合 TOTAL_BAD = 0\n\n安装\n====\n1. 建议先删除或移走旧版 fix1/fix2 的：\n   atmosphere/contents/0100A3A00CC7E000/romfs/\n2. 如果之前手动放过 CLANNAD 的 exefs_patches，也请先移走旧版本，避免重复应用。\n3. 将本补丁中的 atmosphere 文件夹复制到 SD 卡根目录。\n4. 最终应同时存在：\n   atmosphere/contents/0100A3A00CC7E000/romfs/\n   atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix3/{full_module}.ips\n5. 本 IPS 仅针对 CLANNAD v1.0.7 的上述 Module ID。不同更新版本不要强行使用。\n\n建议真机重点检查\n================\n- 标题菜单未选中与选中状态是否仍有重叠。\n- 设置页所有分页、选项值与右侧说明。\n- 保存/读取/返回标题/跳转等系统弹窗。\n- 正文补字字体风格与位置。\n\n说明\n====\n本发布只包含汉化替换资源与针对 v1.0.7 的 IPS 补丁，不包含游戏本体、更新包、密钥或解密材料。\n'''
(release/'README.txt').write_text(readme,encoding='utf-8-sig')
# regenerate hashes including README + QA summary but exclude SHA file itself
entries=[]
for f in sorted(release.rglob('*')):
    if f.is_file() and f.name!='SHA256SUMS.txt':entries.append((sha(f),f.relative_to(release).as_posix(),f.stat().st_size))
(release/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {path}  ({size} bytes)' for h,path,size in entries)+'\n',encoding='utf-8')
print('RELEASE',release)
for h,path,size in entries:print(h,size,path)
print('FILE_COUNT',len(entries)+1)
