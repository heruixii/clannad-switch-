from pathlib import Path
import csv,struct,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/font_package_fix2/FONT.PAK_unpacked';LOG=R/'05_build/font_package_fix2/font_patch_reports.jsonl'
def rows(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def parse(p):
 b=p.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0);cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6
 # draw metrics: cnt records of 3 bytes begin at head, then unicode table
 draw=[tuple(b[head+i*3:head+i*3+3]) for i in range(cnt)];pos=head+cnt*3;cov=set();idx={}
 for cp in range(65536):
  i=struct.unpack_from('<H',b,pos+cp*2)[0]
  if i!=0 or cp==32:cov.add(chr(cp));idx[chr(cp)]=i
 return fs,bs,cnt,cov,idx,draw
zh=''.join(r['zh_text'] for r in rows(R/'03_text/translated/message_targets_complete_v12.tsv'))+''.join(r['zh_text'] for r in rows(R/'03_text/translated/select_targets_complete_v2.tsv'));req={c for c in zh if ord(c)>=128}
maprows=rows(R/'05_build/font_patch_plan/slot_map_v2.tsv');expected={r['new_char']:int(r['index']) for r in maprows};old={r['old_char'] for r in maprows};slotidx=set(expected.values())
infos=sorted(D.glob('info*'));errs=[];res=[];yvals=[]
for p in infos:
 fs,bs,cnt,cov,idx,draw=parse(p); mz=sorted(req-cov,key=ord); badmap=[(c,expected[c],idx.get(c)) for c in expected if idx.get(c)!=expected[c]];oldleft=old&cov
 ys=[draw[i][2] for i in slotidx]; yvals.extend(ys)
 row={'name':p.name,'font_size':fs,'block_size':bs,'char_num':cnt,'missing_zh':len(mz),'bad_slot_map':len(badmap),'old_reclaimed_still_mapped':len(oldleft),'new_slot_y_min':min(ys),'new_slot_y_max':max(ys)};res.append(row)
 if cnt!=7188 or mz or badmap or oldleft or min(ys)!=0 or max(ys)!=0:errs.append(row)
recs=[]
for line in LOG.read_text(encoding='utf-8-sig').splitlines():
 line=line.strip()
 if not line.startswith('{'):continue
 w=json.loads(line); r=w.get('report',w); recs.append((w,r))
repbad=[]
for w,r in recs:
 if r.get('ttf_missing')!=0 or r.get('blank_glyphs') or r.get('alpha_changed_outside_prequant')!=0 or r.get('alpha_changed_outside_output')!=0 or r.get('alpha_mismatch_inside_output')!=0 or r.get('mapping_missing_after') or r.get('char_num_before')!=7188 or r.get('char_num_after')!=7188 or r.get('block_count_before')!=r.get('block_count_after') or r.get('quantization_max_alpha_error',99)>1:repbad.append(w)
families={}
for w,r in recs:families.setdefault(w.get('family','?'),{'count':0,'sources':set()});families[w.get('family','?')]['count']+=1;families[w.get('family','?')]['sources'].add(w.get('source','?'))
families={k:{'count':v['count'],'sources':sorted(v['sources'])} for k,v in families.items()}
summary={'font_files_total':len(list(D.iterdir())),'info_files':len(infos),'reports':len(recs),'report_failures':len(repbad),'required_zh_nonascii':len(req),'info_failures':len(errs),'new_slot_y_min':min(yvals),'new_slot_y_max':max(yvals),'family_sources':families,'info_results':res}
print(json.dumps(summary,ensure_ascii=False,indent=2));(R/'05_build/font_package_fix2/font_final_qa_fix2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
if errs or repbad or len(recs)!=56 or len(infos)!=12 or len(list(D.iterdir()))!=68:raise SystemExit(2)

