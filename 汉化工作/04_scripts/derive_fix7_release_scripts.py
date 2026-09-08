from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
# derive source verifier
s=(R/'04_scripts/verify_release_sources_fix6_v22.py').read_text(encoding='utf-8')
s=s.replace("script_package_fix6/SCRIPT.PAK.out","script_package_fix7/SCRIPT.PAK.out").replace("script_package_fix6/SCRIPT.PAK_unpacked","script_package_fix7/SCRIPT.PAK_unpacked")
s=s.replace("iq=json.loads((R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').read_text(encoding='utf-8'))","iq=json.loads((R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').read_text(encoding='utf-8')); nq=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8'))")
s=s.replace("'title_old_menu_hits':title_bad}","'title_old_menu_hits':title_bad,'name_fix7_total_bad':nq['total_bad'],'name_tomoya_remaining':nq['seen2417_tomoya_remaining'],'name_prompt_old_hits':len(nq['old_name_prompt_hits']),'name_font_missing':nq['font_missing_count']}")
s=s.replace("+aux['title_old_menu_hits']+(0 if aux['config_tab_layer_iou']>=.95 else 1)","+aux['title_old_menu_hits']+aux['name_fix7_total_bad']+aux['name_tomoya_remaining']+aux['name_prompt_old_hits']+aux['name_font_missing']+(0 if aux['config_tab_layer_iou']>=.95 else 1)")
s=s.replace("final_release_sources_verify_fix6.json","final_release_sources_verify_fix7.json")
(R/'04_scripts/verify_release_sources_fix7_v9.py').write_text(s,encoding='utf-8')
# derive release builder
s=(R/'04_scripts/build_release_fix6_v23.py').read_text(encoding='utf-8')
s=s.replace('fix6','fix7').replace("script_package_fix7/SCRIPT.PAK.out","script_package_fix7/SCRIPT.PAK.out")
# replacement above changes source script path because all fix6->fix7; fix7 resources exist for script/exefs only, but some referenced QA keyword fix7 does not. fix back stable resources/QA.
s=s.replace("keyword_fix7/keyword_fix7_qa.json","keyword_fix6/keyword_fix6_qa.json")
s=s.replace("final_release_sources_verify_fix7.json","final_release_sources_verify_fix7.json")
s=s.replace("fix7_exefs/FINAL_IPS_QA_fix7.json","fix7_name_qa.json")
# update README content with fix7 note in front of old text
marker='fix7 重点修复\n============\n'
insert='fix7 重点修复\n============\n1. 主角默认名英文修复\n- 正式剧情 SEEN2417 中存在“朋也 / Tomoya”双语言槽；游戏保持 English UI 状态时会选择 Tomoya。\n- fix7 将正式流程英文槽原位替换为“朋也”，Tomoya 剩余 0。\n- 姓名设置中的两条 Okazaki Tomoya 英文语音提示也原位改为中文。\n- 不修改 Z_TEST 测试脚本，不改变语言状态和配音判定逻辑。\n\n2. 继续完整继承 fix6\n'
s=s.replace(marker,insert,1)
s=s.replace('1. 游戏内剩余按钮中英文重叠','- 游戏内剩余按钮中英文重叠').replace('2. 团子百科底部目录挤在一起','- 团子百科底部目录挤在一起').replace('3. 沿用此前稳定修复','- 沿用此前稳定修复')
s=s.replace("summary={'release':'fix7','target_version':'v1.0.7','module_id':full,'source_total_bad':qa['TOTAL_BAD'],'ips':iq,'keyword':kq}","summary={'release':'fix7','target_version':'v1.0.7','module_id':full,'source_total_bad':qa['TOTAL_BAD'],'name_qa':iq,'keyword':kq}")
(R/'04_scripts/build_release_fix7_v10.py').write_text(s,encoding='utf-8')
print('scripts written')
