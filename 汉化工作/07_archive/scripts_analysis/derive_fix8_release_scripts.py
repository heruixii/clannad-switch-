from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
# source verifier from fix7; PAKs unchanged, add fix8 IPS gate
s=(R/'04_scripts/verify_release_sources_fix7_v9.py').read_text(encoding='utf-8')
s=s.replace("nq=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8'))","nq=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8')); rq=json.loads((R/'05_build/fix8_exefs/FINAL_IPS_QA_fix8.json').read_text(encoding='utf-8'))")
s=s.replace("'name_font_missing':nq['font_missing_count']}","'name_font_missing':nq['font_missing_count'],'runtime_name_fix8_total_bad':rq['total_bad'],'runtime_name_sites_bad':len(rq['runtime_site_bad'])}")
s=s.replace("+aux['name_font_missing']+(0 if aux['config_tab_layer_iou']>=.95 else 1)","+aux['name_font_missing']+aux['runtime_name_fix8_total_bad']+aux['runtime_name_sites_bad']+(0 if aux['config_tab_layer_iou']>=.95 else 1)")
s=s.replace('final_release_sources_verify_fix7.json','final_release_sources_verify_fix8.json')
(R/'04_scripts/verify_release_sources_fix8_v21.py').write_text(s,encoding='utf-8')
# release builder derived manually from fix7
s=(R/'04_scripts/build_release_fix7_v10.py').read_text(encoding='utf-8')
s=s.replace('fix7','fix8')
# PAK source stays script_package_fix7; keyword stays fix6; new exefs is fix8.
s=s.replace('script_package_fix8/SCRIPT.PAK.out','script_package_fix7/SCRIPT.PAK.out')
s=s.replace('keyword_fix8/keyword_fix6_qa.json','keyword_fix6/keyword_fix6_qa.json')
s=s.replace("fix8_name_qa.json","fix8_exefs/FINAL_IPS_QA_fix8.json")
# README wording: prepend runtime root cause and ensure old dirs range.
needle='fix8 重点修复\n============\n'
intro='fix8 重点修复\n============\n1. 主角姓名英文的运行时根修复\n- fix7 只改了脚本初始化槽，但实机仍显示英文，说明最终姓名来自持久化姓名表。\n- 反汇编确认姓名系统有 JP 与 EN 两套独立当前/默认槽，EN 槽相对 JP 槽固定偏移 0x22。\n- 因汉化为保持剧情/UI稳定而让全局 UI 继续处于 English=1，原游戏会读取 EN 姓名槽，因此旧存档中的 Roman 姓名持续覆盖脚本。\n- fix8 不改全局语言，只在姓名子系统的 7 个确定语言选择点强制索引 0：剧情姓名展开、默认名比较、姓名编辑显示/编辑、恢复默认写槽。\n- 因此旧存档也会直接从 JP/中文姓名槽读取，不依赖重新开档。\n\n2. 完整继承 fix7/fix6 及此前修复\n'
s=s.replace(needle,intro,1)
s=s.replace('1. 主角默认名英文修复','- fix7 主角默认名初始化/提示修复').replace('2. 继续完整继承 fix6','- fix6 按钮和团子百科目录修复')
# Fix references that global replacement changed to nonexistent stable resources.
s=s.replace("fix8_exefs/FINAL_IPS_QA_fix8.json','keyword':kq", "fix8_exefs/FINAL_IPS_QA_fix8.json','keyword':kq")
(R/'04_scripts/build_release_fix8_v22.py').write_text(s,encoding='utf-8')
print('derived fix8 scripts')
