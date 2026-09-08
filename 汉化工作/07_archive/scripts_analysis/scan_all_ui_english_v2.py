from pathlib import Path
from PIL import Image
import numpy as np,easyocr,subprocess,csv,re,shutil
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; OUT=R/'05_build/ui_fullscan_png'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
sources=[('SYSCG',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'),('PARTS',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'),('SYSCG2',R/'03_text/ui_work/SYSCG2.PAK_unpacked')]
files=[]
for pak,d in sources:
 if not d.exists(): continue
 for src in sorted(x for x in d.iterdir() if x.is_file()):
  out=OUT/f'{pak}__{src.name}.png'
  z=subprocess.run([str(EXE),'export',str(src),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if z.returncode==0 and out.exists(): files.append((pak,src.name,out))
print('EXPORTED',len(files),flush=True)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False); rows=[]
for idx,(pak,name,p) in enumerate(files,1):
 im=Image.open(p).convert('RGBA'); bg=Image.new('RGBA',im.size,(0,0,0,255)); bg.alpha_composite(im); rgb=bg.convert('RGB'); W,H=rgb.size
 chunks=[]
 if H>1400:
  y=0
  while y<H:
   y2=min(H,y+1200); chunks.append((y,np.array(rgb.crop((0,y,W,y2))))); 
   if y2==H: break
   y=y2-80
 else: chunks=[(0,np.array(rgb))]
 for y0,a in chunks:
  try:res=rd.readtext(a,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.2,text_threshold=.42,low_text=.18,link_threshold=.22)
  except Exception:res=[]
  for box,text,conf in res:
   clean=text.strip()
   letters=sum(c.isalpha() for c in clean)
   if conf>=.45 and letters>=3 and len(clean)<=80:
    x1=min(x for x,y in box);y1=min(y for x,y in box)+y0;x2=max(x for x,y in box);y2=max(y for x,y in box)+y0
    rows.append([pak,name,clean,float(conf),x1,y1,x2,y2,W,H])
 if idx%25==0: print('OCR',idx,'/',len(files),'hits',len(rows),flush=True)
with (R/'05_build/ui_fullscan_english.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['pak','asset','text','conf','x1','y1','x2','y2','width','height']);w.writerows(rows)
print('DONE HITS',len(rows))
for r in rows: print('\t'.join(map(str,r[:4])))
