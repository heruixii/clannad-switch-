from pathlib import Path
import csv,collections,json,re
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def norm(s):
 return (s or '').replace('\\r','').replace('\r','').strip()
sel=rd(S); pc=rd(PC)
idx=collections.defaultdict(list)
for r in pc:
 if r.get('jp_text') and r.get('zh_text'):
  idx[norm(r['jp_text'])].append(r)
unique={r['jp_text'] for r in sel};exact=0;details=[]
for s in sorted(unique):
 c=idx.get(norm(s),[])
 if c:
  exact+=1;details.append((s,c[0]['zh_text'],len(c),c[0]['scene'],c[0]['status']))
print(json.dumps({'select_rows':len(sel),'unique_jp':len(unique),'pc_exact_unique_strings':exact},ensure_ascii=False,indent=2))
for x in details[:100]:print('JP=',x[0],'\nZH=',x[1],' n=',x[2],' scene=',x[3],' status=',x[4],sep='')
