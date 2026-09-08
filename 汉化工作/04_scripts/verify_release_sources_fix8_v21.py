from pathlib import Path
import struct,json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
items=[
 ('SCRIPT',R/'05_build/script_package_fix7/SCRIPT.PAK.out',R/'05_build/script_package_fix7/SCRIPT.PAK_unpacked'),
 ('FONT',R/'05_build/font_package_fix2/FONT.PAK.out',R/'05_build/font_package_fix2/FONT.PAK_unpacked'),
 ('SYSCG',R/'05_build/ui_packages_v1/SYSCG.PAK.out',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'),
 ('PARTS',R/'05_build/ui_packages_fix5/PARTS.PAK.out',R/'05_build/ui_packages_fix5/PARTS.PAK_unpacked'),
 ('MANUAL',R/'05_build/ui_packages_v1/MANUAL.PAK.out',R/'05_build/ui_packages_v1/MANUAL.PAK_unpacked'),
 ('OTHCG',R/'05_build/OTHCG.PAK.out',R/'05_build/othcg_chs_unpacked'),
]
def parse_named(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 q=u(pos-4);names=[]
 for _ in range(fc):z=b.find(b'\0',q,hl);names.append(b[q:z].decode('utf-8'));q=z+1
 return b,hl,fc,idstart,bs,pos,names
report={};total=0
for label,p,d in items:
 b,hl,fc,idstart,bs,pos,names=parse_named(p);bad=[];missing=[];over=[];prev=hl
 for i,n in enumerate(names):
  bo,ln=struct.unpack_from('<II',b,pos+i*8);off=bo*bs
  if ln and off<prev:over.append([n,off,prev])
  if ln:prev=max(prev,off+ln)
  q=d/n
  if not q.exists():missing.append(n);continue
  if b[off:off+ln]!=q.read_bytes():bad.append(n)
 total+=len(bad)+len(missing)+len(over);report[label]={'entries':fc,'bad':bad,'missing':missing,'overlap':over,'size':len(b),'sha256':hashlib.sha256(b).hexdigest().upper()};print(label,'bad',len(bad),'missing',len(missing),'overlap',len(over),report[label]['sha256'])
# PARTS2 sparse
p=R/'05_build/parts2_fix4/PARTS2.PAK.out';b=p.read_bytes();hl,fc,idstart,bs,*_=struct.unpack_from('<9I',b,0);pos=40;orig=(R/'03_text/ui_work/PARTS2.PAK').read_bytes();expected=[]
for i in range(fc):bo,ln=struct.unpack_from('<II',orig,pos+i*8);expected.append(orig[bo*bs:bo*bs+ln] if (bo or ln) else b'')
expected[8]=(R/'05_build/config_fix4/PARTS2_CONFIG_BG_CHS').read_bytes();expected[9]=expected[8];expected[12]=(R/'05_build/config_fix4/PARTS2_CONFIG_TAB_CHS').read_bytes();expected[13]=expected[12];bad=[]
for i,exp in enumerate(expected):bo,ln=struct.unpack_from('<II',b,pos+i*8);got=b[bo*bs:bo*bs+ln] if (bo or ln) else b'';bad += [i] if got!=exp else []
report['PARTS2']={'entries':fc,'bad':bad,'size':len(b),'sha256':hashlib.sha256(b).hexdigest().upper()};total+=len(bad);print('PARTS2 bad',len(bad),report['PARTS2']['sha256'])
# auxiliary QA
kq=json.loads((R/'05_build/keyword_fix6/keyword_fix6_qa.json').read_text(encoding='utf-8'));iq=json.loads((R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').read_text(encoding='utf-8')); nq=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8')); rq=json.loads((R/'05_build/fix8_exefs/FINAL_IPS_QA_fix8.json').read_text(encoding='utf-8'));bq=json.loads((R/'05_build/button_fix5/button_fix5_ocr_qa.json').read_text(encoding='utf-8'));fq=json.loads((R/'05_build/font_package_fix2/font_final_qa_fix2.json').read_text(encoding='utf-8'));cq=json.loads((R/'05_build/config_fix4_static_qa.json').read_text(encoding='utf-8'));tq=json.loads((R/'05_build/title_fix3_ocr_qa.json').read_text(encoding='utf-8'))
title_bad=sum(len(v.get('hits',[])) for v in tq.values())
aux={'keyword_records':kq['records'],'keyword_parse_bad':len(kq['parse_bad']),'keyword_visible_english_residue':len(kq['visible_old_english_residue']),'keyword_sort_keys_restored':kq['sort_keys_restored'],'keyword_directory_groups':kq['directory_groups'],'button_static_english_bad':len(bq['bad']),'dynamic_button_old_refs_remaining':iq['old_button_ref_count'],'dynamic_button_site_bad':len(iq['site_bad']),'ips_inherited_config_refs_remaining':iq['inherited_moved_config_refs_remaining'],'ips_inherited_system_refs_remaining':iq['inherited_system_refs_remaining'],'ips_outside_changes':iq['changed_outside_ips_ranges'],'font_report_failures':fq['report_failures'],'font_info_failures':fq['info_failures'],'font_required_zh_missing':sum(x['missing_zh'] for x in fq['info_results']),'config_static_english_bad':len(cq['english_bad']),'config_tab_layer_iou':cq['tab_layer_iou_after_14px'],'title_old_menu_hits':title_bad,'name_fix7_total_bad':nq['total_bad'],'name_tomoya_remaining':nq['seen2417_tomoya_remaining'],'name_prompt_old_hits':len(nq['old_name_prompt_hits']),'name_font_missing':nq['font_missing_count'],'runtime_name_fix8_total_bad':rq['total_bad'],'runtime_name_sites_bad':len(rq['runtime_site_bad'])}
auxbad=aux['keyword_parse_bad']+aux['keyword_visible_english_residue']+(0 if aux['keyword_sort_keys_restored'] else 1)+(0 if aux['keyword_directory_groups']==22 else 1)+aux['button_static_english_bad']+aux['dynamic_button_old_refs_remaining']+aux['dynamic_button_site_bad']+aux['ips_inherited_config_refs_remaining']+aux['ips_inherited_system_refs_remaining']+aux['ips_outside_changes']+aux['font_report_failures']+aux['font_info_failures']+aux['font_required_zh_missing']+aux['config_static_english_bad']+aux['title_old_menu_hits']+aux['name_fix7_total_bad']+aux['name_tomoya_remaining']+aux['name_prompt_old_hits']+aux['name_font_missing']+aux['runtime_name_fix8_total_bad']+aux['runtime_name_sites_bad']+(0 if aux['config_tab_layer_iou']>=.95 else 1)
total+=auxbad;report['AUX_QA']=aux;report['TOTAL_BAD']=total
(R/'05_build/final_release_sources_verify_fix8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('AUX',json.dumps(aux,ensure_ascii=False));print('TOTAL_BAD',total);raise SystemExit(1 if total else 0)
