from pathlib import Path
import csv,sys,collections,json,re
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'
with S.open('r',encoding='utf-8-sig',newline='') as f: sw=list(csv.DictReader(f,delimiter='\t'))
swb=collections.defaultdict(list)
for r in sw: swb[r['scene']].append(r)

def blocks(path):
 dec,h=decompress_blob(path.read_bytes()); out=[]
 for i in range(len(dec)-8):
  if not(dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2):continue
  func=int.from_bytes(dec[i+3:i+5],'little')
  if func not in (0,1,2,3,10):continue
  argc=int.from_bytes(dec[i+5:i+7],'little')
  op=dec.find(b'{',i+8,min(len(dec),i+300));
  if op<0:continue
  cl=dec.find(b'}',op+1,min(len(dec),op+8000));
  if cl<0:continue
  b=dec[op+1:cl]; qs=[]; q=0
  while q<len(b):
   a=b.find(b'"',q)
   if a<0:break
   e=b.find(b'"',a+1)
   if e<0:break
   raw=b[a+1:e]
   try: txt=raw.decode('gbk')
   except: txt=None
   qs.append(txt);q=e+1
  out.append({'off':i,'argc':argc,'quotes':qs})
 return out
base=ROOT/'03_text/pc_zh/raw'; rec=ROOT/'03_text/pc_zh/recovered'; pcb={}
for p in base.glob('SEEN*.TXT'):
 use=(rec/p.name) if (rec/p.name).exists() else p
 try: pcb[p.stem]=blocks(use)
 except: pass
mapped=[]; bad=[]
for sc, ss in swb.items():
 ps=pcb.get(sc,[])
 if len(ss)!=len(ps):continue
 for k,(s,p) in enumerate(zip(ss,ps)):
  nopt=s['jp_text'].count('$d')+1
  if len(p['quotes'])==p['argc']==nopt and all(x is not None for x in p['quotes']):
   mapped.append((sc,s['code_index'],'$d'.join(p['quotes']),nopt))
  else: bad.append((sc,k,s['code_index'],nopt,p['argc'],len(p['quotes'])))
print(json.dumps({'equal_scene_select_rows':sum(len(v) for sc,v in swb.items() if len(v)==len(pcb.get(sc,[]))),'mapped':len(mapped),'bad':len(bad)},ensure_ascii=False,indent=2))
print('bad',bad)
out=ROOT/'03_text/translated/select_pc_equal_map.tsv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['scene','code_index','zh_text','option_count']);w.writerows(mapped)
print(out)
