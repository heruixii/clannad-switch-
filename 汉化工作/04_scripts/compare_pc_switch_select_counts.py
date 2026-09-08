from pathlib import Path
import csv,sys,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'
with S.open('r',encoding='utf-8-sig',newline='') as f: sw=list(csv.DictReader(f,delimiter='\t'))
swc=collections.Counter(r['scene'] for r in sw)
pc={}
base=ROOT/'03_text/pc_zh/raw'; rec=ROOT/'03_text/pc_zh/recovered'
for p in sorted(base.glob('SEEN*.TXT')):
 rp=rec/p.name; use=rp if rp.exists() else p
 try: dec,h=decompress_blob(use.read_bytes())
 except: continue
 n=0
 for i in range(len(dec)-8):
  if dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2 and int.from_bytes(dec[i+3:i+5],'little') in (0,1,2,3,10): n+=1
 if n: pc[p.stem]=n
scenes=sorted(set(swc)|set(pc))
rows=[]
for sc in scenes:
 if swc[sc] or pc.get(sc,0): rows.append((sc,swc[sc],pc.get(sc,0),swc[sc]-pc.get(sc,0)))
print('switch total',sum(swc.values()),'pc total',sum(pc.values()),'scenes',len(rows))
from collections import Counter
print('diffs',Counter(d for _,_,_,d in rows))
for r in rows:
 if r[3]!=0: print('\t'.join(map(str,r)))
