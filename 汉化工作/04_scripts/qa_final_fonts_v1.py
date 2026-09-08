from pathlib import Path
import csv,struct,json,collections
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
D=R/'05_build/font_package/FONT.PAK_unpacked'
LOG=R/'05_build/font_package/font_patch_reports.jsonl'
def rows(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def parse(p):
 b=p.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0);cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6;pos=head+cnt*3;cov=set();idx={}
 for cp in range(65536):
  i=struct.unpack_from('<H',b,pos+cp*2)[0]
  if i!=0 or cp==32:cov.add(chr(cp));idx[chr(cp)]=i
 return fs,bs,cnt,cov,idx
# required final zh and original visible JP/EN
zh=''.join(r['zh_text'] for r in rows(R/'03_text/translated/message_targets_complete_v12.tsv'))+''.join(r['zh_text'] for r in rows(R/'03_text/translated/select_targets_complete_v2.tsv'))
req={c for c in zh if ord(c)>=128}
preserve=set()
for p,cols in [(R/'03_text/switch_extracted/switch_messages.tsv',('jp_text','en_text')),(R/'03_text/switch_extracted/switch_selects.tsv',('jp_text','en_text'))]:
 for r in rows(p):
  for c in cols:preserve.update(r[c])
preserve={c for c in preserve if ord(c)>=32 and ord(c)<65536}
maprows=rows(R/'05_build/font_patch_plan/slot_map_v2.tsv')
expected={r['new_char']:int(r['index']) for r in maprows}; old={r['old_char'] for r in maprows}
infos=sorted(D.glob('info*'));out=[];errs=[]
for p in infos:
 fs,bs,cnt,cov,idx=parse(p);mz=sorted(req-cov,key=ord);mp=sorted(preserve-cov,key=ord);badmap=[(c,expected[c],idx.get(c)) for c in expected if idx.get(c)!=expected[c]];oldleft=sorted(old&cov,key=ord)
 row={'name':p.name,'font_size':fs,'block_size':bs,'char_num':cnt,'coverage':len(cov),'missing_zh':len(mz),'missing_preserve':len(mp),'bad_slot_map':len(badmap),'old_reclaimed_still_mapped':len(oldleft)};out.append(row)
 if cnt!=7188 or mz or mp or badmap or oldleft:errs.append((p.name,row,''.join(mz[:30]),''.join(mp[:30]),badmap[:3],''.join(oldleft[:30])))
# reports
reports=[]
for line in LOG.read_text(encoding='utf-8-sig').splitlines():
 line=line.strip()
 if line.startswith('{'):reports.append(json.loads(line))
repbad=[r for r in reports if r.get('ttf_missing')!=0 or r.get('blank_glyphs') or r.get('alpha_changed_outside_prequant')!=0 or r.get('alpha_changed_outside_output')!=0 or r.get('alpha_mismatch_inside_output')!=0 or r.get('mapping_missing_after') or r.get('char_num_before')!=7188 or r.get('char_num_after')!=7188 or r.get('block_count_before')!=r.get('block_count_after') or r.get('quantization_max_alpha_error',99)>1]
summary={'font_files_total':len(list(D.iterdir())),'info_files':len(infos),'reports':len(reports),'report_failures':len(repbad),'required_zh_nonascii':len(req),'preserved_visible_chars':len(preserve),'info_results':out,'info_failures':len(errs),'max_quantization_alpha_error':max((r.get('quantization_max_alpha_error',0) for r in reports),default=0),'max_mean_quantization_alpha_error':max((r.get('quantization_mean_alpha_error',0) for r in reports),default=0)}
print(json.dumps(summary,ensure_ascii=False,indent=2));print('ERRORS',errs[:5]);print('REPORT_BAD',repbad[:3])
(R/'05_build/font_package/font_final_qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
if errs or repbad or len(reports)!=56 or len(infos)!=12 or len(list(D.iterdir()))!=68:raise SystemExit(2)
