from pathlib import Path
from PIL import Image
import numpy as np,csv,struct,json,subprocess,os
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); T=R/'05_build/ui_png_zh_v3'; C=R/'05_build/ui_cz_v3'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; TMP=R/'05_build/ui_cz_verify_png';TMP.mkdir(parents=True,exist_ok=True)
rows=[]; bad=[]
for pakdir in sorted([p for p in C.iterdir() if p.is_dir()]):
 for cz in sorted(pakdir.iterdir()):
  if not cz.is_file():continue
  target=T/(cz.name+'.png'); out=TMP/(pakdir.name+'__'+cz.name+'.png')
  subprocess.run([str(EXE),'export',str(cz),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
  a=np.array(Image.open(target).convert('RGBA'),dtype=np.int16);b=np.array(Image.open(out).convert('RGBA'),dtype=np.int16)
  if a.shape!=b.shape:
   bad.append((pakdir.name,cz.name,'shape'));continue
  d=np.abs(a-b); rgb=d[:,:,:3]; al=d[:,:,3]
  changed=np.any(d>0,axis=2)
  b0=cz.read_bytes();typ=b0[:3].decode('ascii','replace')
  rec={'pak':pakdir.name,'asset':cz.name,'type':typ,'width':a.shape[1],'height':a.shape[0],'diff_pixels':int(changed.sum()),'diff_ratio':float(changed.mean()),'max_rgb':int(rgb.max()),'mean_rgb':float(rgb.mean()),'max_alpha':int(al.max()),'mean_alpha':float(al.mean()),'alpha_diff_pixels':int((al>0).sum())}
  rows.append(rec)
  # tolerant safety: dimensions exact, mean RGB <=4, mean alpha <=2, catastrophic alpha changes disallowed
  if rec['mean_rgb']>4.0 or rec['mean_alpha']>2.0 or rec['max_alpha']>80:
   bad.append((pakdir.name,cz.name,rec))
with (R/'05_build/ui_cz_quantization_qa.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t');w.writeheader();w.writerows(rows)
from collections import Counter
print(json.dumps({'assets':len(rows),'types':Counter(r['type'] for r in rows),'bad':len(bad),'max_mean_rgb':max(r['mean_rgb'] for r in rows),'max_mean_alpha':max(r['mean_alpha'] for r in rows),'max_alpha':max(r['max_alpha'] for r in rows),'worst_rgb':sorted(rows,key=lambda r:r['mean_rgb'],reverse=True)[:10],'worst_alpha':sorted(rows,key=lambda r:r['mean_alpha'],reverse=True)[:10]},ensure_ascii=False,indent=2,default=lambda x:dict(x)))
for x in bad[:30]:print('BAD',x)
raise SystemExit(2 if bad else 0)
