from pathlib import Path
import csv,struct,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
def rows(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
b=(R/'03_text/switch_work/paks/FONT.PAK_unpacked/info24').read_bytes();third=struct.unpack_from('<H',b,4)[0];cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6;pos=head+cnt*3;idx=['\0']*cnt
for cp in range(65536):
 i=struct.unpack_from('<H',b,pos+cp*2)[0]
 if i<cnt and (i!=0 or cp==32):idx[i]=chr(cp)
used=set()
for p,cols in [(R/'03_text/switch_extracted/switch_messages.tsv',('jp_text','en_text')),(R/'03_text/switch_extracted/switch_selects.tsv',('jp_text','en_text'))]:
 for r in rows(p):
  for c in cols:used.update(r[c])
for a,z in [(0x20,0x100),(0x3000,0x3100),(0xFF00,0xFFF0)]:
 used.update(chr(cp) for cp in range(a,z))
zh=''.join(r['zh_text'] for r in rows(R/'03_text/translated/message_targets_complete_v12.tsv'))+''.join(r['zh_text'] for r in rows(R/'03_text/translated/select_targets_complete_v2.tsv'))
req=set(c for c in zh if ord(c)>=128); missing=sorted(req-set(idx),key=ord)
rep={}
for th in [7000,6800,6600,6400,6200,6000,5800,5600,5400,5200,5000,4800,4600,4400,4200,4000]:
 cand=[(i,idx[i]) for i in range(cnt-1,th-1,-1) if idx[i] not in ('','\0') and idx[i] not in used and idx[i] not in req]
 rep[th]=len(cand)
print(json.dumps({'char_num':cnt,'missing':len(missing),'candidates_by_min_index':rep},ensure_ascii=False,indent=2))
# choose highest threshold with enough candidates
oks=[th for th,n in rep.items() if n>=len(missing)];print('BEST_THRESHOLD',max(oks) if oks else None)
