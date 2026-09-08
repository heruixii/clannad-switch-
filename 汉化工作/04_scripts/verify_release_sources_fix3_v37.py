from pathlib import Path
import struct,json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
items=[
 ('SCRIPT',R/'05_build/script_package/SCRIPT.PAK.out',R/'05_build/script_package/SCRIPT.PAK_unpacked'),
 ('FONT',R/'05_build/font_package_fix2/FONT.PAK.out',R/'05_build/font_package_fix2/FONT.PAK_unpacked'),
 ('SYSCG',R/'05_build/ui_packages_v1/SYSCG.PAK.out',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'),
 ('PARTS',R/'05_build/ui_packages_v1/PARTS.PAK.out',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'),
 ('MANUAL',R/'05_build/ui_packages_v1/MANUAL.PAK.out',R/'05_build/ui_packages_v1/MANUAL.PAK_unpacked'),
 ('OTHCG',R/'05_build/OTHCG.PAK.out',R/'05_build/othcg_chs_unpacked'),
]
def parse(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 if pos+8*fc>hl:raise ValueError('offset table')
 named=bool(flags&512);names=[]
 if named:
  q=u(pos-4)
  for _ in range(fc):z=b.find(b'\0',q,hl);names.append(b[q:z].decode('utf-8'));q=z+1
 else:names=[str(i) for i in range(fc)]
 rows=[]
 for i,n in enumerate(names):bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((n,bo*bs,ln,bo))
 return b,hl,fc,idstart,bs,rows,pos
report={};total=0
for label,p,d in items:
 b,hl,fc,idstart,bs,rows,pos=parse(p);bad=[];missing=[];overlap=[];prev=hl
 for n,off,ln,bo in rows:
  if off%bs:bad.append([n,'unaligned',off])
  if ln and off<prev:overlap.append([n,off,prev])
  if ln:prev=max(prev,off+ln)
  q=d/n
  if not q.exists():missing.append(n);continue
  if b[off:off+ln]!=q.read_bytes():bad.append([n,'content'])
 total+=len(bad)+len(missing)+len(overlap)
 report[label]={'entries':fc,'size':len(b),'bad':bad,'missing':missing,'overlap':overlap,'sha256':hashlib.sha256(b).hexdigest().upper()}
 print(label,'entries',fc,'bad',len(bad),'missing',len(missing),'overlap',len(overlap),'sha',report[label]['sha256'])
# PARTS2 sparse specialized
p=R/'05_build/parts2_fix2/PARTS2.PAK.out';b=p.read_bytes();hl,fc,idstart,bs,*_=struct.unpack_from('<9I',b,0);pos=40;rows=[]
for i in range(fc):
 bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((str(i),bo*bs,ln,bo))
bad=[];nz=[]
expected={8:(R/'05_build/parts2_fix2/CONFIG_BG_CHS').read_bytes(),9:(R/'05_build/parts2_fix2/CONFIG_BG_CHS').read_bytes(),12:(R/'05_build/parts2_fix2/CONFIG_TAB_CHS').read_bytes(),13:(R/'05_build/parts2_fix2/CONFIG_TAB_CHS').read_bytes(),116:(R/'05_build/parts2_sparse/EXTRA_64116').read_bytes()}
for i,(n,off,ln,bo) in enumerate(rows):
 exp=expected.get(i,b'')
 got=b[off:off+ln] if (bo or ln) else b''
 if got!=exp:bad.append([i,idstart+i,'content',len(got),len(exp)])
 if exp:nz.append([i,idstart+i,len(exp),bo])
report['PARTS2']={'entries':fc,'size':len(b),'bad':bad,'nonzero':nz,'sha256':hashlib.sha256(b).hexdigest().upper()};total+=len(bad)
print('PARTS2 entries',fc,'bad',len(bad),'sha',report['PARTS2']['sha256'])
# auxiliary QA gates
fq=json.loads((R/'05_build/font_package_fix2/font_final_qa_fix2.json').read_text(encoding='utf-8'));iq=json.loads((R/'05_build/fix3_exefs/FINAL_IPS_QA_fix3.json').read_text(encoding='utf-8'));tq=json.loads((R/'05_build/title_fix3_ocr_qa.json').read_text(encoding='utf-8'));pq=json.loads((R/'05_build/parts2_fix2/parts2_config_ocr_verify.json').read_text(encoding='utf-8')) if (R/'05_build/parts2_fix2/parts2_config_ocr_verify.json').exists() else {'bad':[]}
title_hits=sum(len(v.get('hits',[])) for v in tq.values());aux={'font_report_failures':fq['report_failures'],'font_info_failures':fq['info_failures'],'font_required_zh_missing':sum(x['missing_zh'] for x in fq['info_results']),'font_new_slot_y_min':fq['new_slot_y_min'],'font_new_slot_y_max':fq['new_slot_y_max'],'ips_config_bad':iq['config_bad'],'ips_system_bad':iq['system_bad'],'title_old_menu_hits':title_hits,'parts2_ocr_bad':len(pq.get('bad',[]))}
aux_bad=aux['font_report_failures']+aux['font_info_failures']+aux['font_required_zh_missing']+aux['ips_config_bad']+aux['ips_system_bad']+aux['title_old_menu_hits']+aux['parts2_ocr_bad'];total+=aux_bad
report['AUX_QA']=aux;report['TOTAL_BAD']=total
(R/'05_build/final_release_sources_verify_fix3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('AUX',json.dumps(aux,ensure_ascii=False));print('TOTAL_BAD',total)
raise SystemExit(1 if total else 0)
