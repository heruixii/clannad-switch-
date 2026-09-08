from pathlib import Path
from PIL import Image
import numpy as np,csv,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); ORIG=R/'05_build/ui_png_en'; VER=R/'05_build/ui_cz_verify_png'; C=R/'05_build/ui_cz_v3'; TAB=R/'03_text/ui_work/ui_ocr_zh_v3.tsv'
with TAB.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
by={}
for r in rows:
 if r['render']=='1':by.setdefault(r['asset'],[]).append(r)
res=[];bad=[]
for pakdir in C.iterdir():
 if not pakdir.is_dir():continue
 for cz in pakdir.iterdir():
  if not cz.is_file():continue
  orig=ORIG/(cz.name+'.png'); ver=VER/(pakdir.name+'__'+cz.name+'.png')
  if not ver.exists():continue
  a=np.array(Image.open(orig).convert('RGBA'),dtype=np.int16);b=np.array(Image.open(ver).convert('RGBA'),dtype=np.int16)
  mask=np.zeros(a.shape[:2],bool)
  for r in by.get(cz.name,[]):
   x1=max(0,int(float(r['x1']))-8);y1=max(0,int(float(r['y1']))-6);x2=min(a.shape[1],int(float(r['x2']))+8);y2=min(a.shape[0],int(float(r['y2']))+6);mask[y1:y2,x1:x2]=True
  d=np.abs(a-b); outside=~mask
  if outside.any():
   od=d[outside]; outside_mean=float(od.mean()); outside_max=int(od.max()); outside_changed=float(np.any(d>0,axis=2)[outside].mean())
  else:outside_mean=0;outside_max=0;outside_changed=0
  inside_changed=float(np.any(d>0,axis=2)[mask].mean()) if mask.any() else 0
  typ=cz.read_bytes()[:3].decode('ascii','replace')
  rec={'pak':pakdir.name,'asset':cz.name,'type':typ,'outside_mean_rgba':outside_mean,'outside_max':outside_max,'outside_changed_ratio':outside_changed,'inside_changed_ratio':inside_changed,'mask_ratio':float(mask.mean())};res.append(rec)
  # outside should be nearly exact; tolerate palette rounding <1 avg and <2% pixels
  if outside_mean>1.0 or outside_changed>0.02:bad.append(rec)
print(json.dumps({'assets':len(res),'bad':len(bad),'max_outside_mean':max(r['outside_mean_rgba'] for r in res),'max_outside_changed':max(r['outside_changed_ratio'] for r in res),'worst':sorted(res,key=lambda r:(r['outside_mean_rgba'],r['outside_changed_ratio']),reverse=True)[:12]},ensure_ascii=False,indent=2))
for r in bad[:30]:print('BAD',r)
with (R/'05_build/ui_cz_outside_qa.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=res[0].keys(),delimiter='\t');w.writeheader();w.writerows(res)
raise SystemExit(2 if bad else 0)
