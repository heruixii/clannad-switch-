from pathlib import Path
import csv,struct,json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
def rows(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def parse(p):
 b=p.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0);cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6;pos=head+cnt*3;idx=['\0']*cnt
 for cp in range(65536):
  i=struct.unpack_from('<H',b,pos+cp*2)[0]
  if i<cnt and (i!=0 or cp==32):idx[i]=chr(cp)
 return fs,bs,cnt,idx
infos=sorted((R/'03_text/switch_work/paks/FONT.PAK_unpacked').glob('info*'))
base=parse(infos[0]); mismatch=[]
for p in infos[1:]:
 x=parse(p)
 if x[2]!=base[2] or x[3]!=base[3]:mismatch.append(p.name)
used=set()
for p,cols in [(R/'03_text/switch_extracted/switch_messages.tsv',('jp_text','en_text')),(R/'03_text/switch_extracted/switch_selects.tsv',('jp_text','en_text'))]:
 for r in rows(p):
  for c in cols:used.update(r[c])
for a,z in [(0x20,0x100),(0x3000,0x3100),(0xFF00,0xFFF0)]:used.update(chr(cp) for cp in range(a,z))
zh=''.join(r['zh_text'] for r in rows(R/'03_text/translated/message_targets_complete_v12.tsv'))+''.join(r['zh_text'] for r in rows(R/'03_text/translated/select_targets_complete_v2.tsv'))
req=set(c for c in zh if ord(c)>=128);missing=sorted(req-set(base[3]),key=ord)
cand=[(i,base[3][i]) for i in range(base[2]-1,5599,-1) if base[3][i] not in ('','\0') and base[3][i] not in used and base[3][i] not in req]
sel=cand[:len(missing)]
out=R/'05_build/font_patch_plan';out.mkdir(parents=True,exist_ok=True)
with (out/'slot_map_v2.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['index','old_char','new_char','old_cp','new_cp'])
 for (i,o),n in zip(sel,missing):w.writerow([i,o,n,f'U+{ord(o):04X}',f'U+{ord(n):04X}'])
(out/'missing_chars_v2.txt').write_text(''.join(missing),encoding='utf-8')
summary={'info_files':len(infos),'mapping_mismatch_infos':mismatch,'char_num':base[2],'threshold':5600,'candidate_count':len(cand),'missing_count':len(missing),'selected_count':len(sel),'selected_min_index':min(i for i,_ in sel),'selected_max_index':max(i for i,_ in sel),'selected_old_preview':''.join(o for _,o in sel[:100]),'new_preview':''.join(missing[:100])}
(out/'summary_v2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if mismatch or len(sel)!=len(missing):raise SystemExit(2)
