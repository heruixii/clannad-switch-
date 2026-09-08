from pathlib import Path
import easyocr,numpy as np
from PIL import Image
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/config_probe_png'; rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for p in sorted(D.glob('*.png')):
 im=np.array(Image.open(p).convert('RGB')); H,W=im.shape[:2]; chunks=[]
 if H>1300:
  for y in range(0,H,1100): chunks.append((y,im[y:min(H,y+1200)]))
 else:chunks=[(0,im)]
 out=[]
 for y0,a in chunks:
  try:r=rd.readtext(a,detail=1,paragraph=False,canvas_size=3500,mag_ratio=1.5,text_threshold=.35,low_text=.15,link_threshold=.2)
  except Exception:r=[]
  for box,text,conf in r:
   if conf>=.12:out.append((min(y for x,y in box)+y0,min(x for x,y in box),conf,text))
 print('\n###',p.stem,(W,H))
 for y,x,c,t in sorted(out):print(f'{c:.3f}\t{x:.0f},{y:.0f}\t{t}')
