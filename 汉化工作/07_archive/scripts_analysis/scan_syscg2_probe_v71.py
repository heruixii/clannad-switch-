from pathlib import Path
from PIL import Image
import numpy as np,easyocr,csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/syscg2_probe'; files=sorted(D.glob('ID_*.png'))
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False);rows=[]
for p in files:
 im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);a=np.array(bg.convert('RGB'))
 try:res=rd.readtext(a,detail=1,paragraph=False,canvas_size=1600,mag_ratio=2.0,text_threshold=.42,low_text=.18,link_threshold=.22)
 except Exception:res=[]
 for box,text,conf in res:
  t=text.strip();letters=sum(c.isalpha() for c in t)
  if conf>=.40 and letters>=3: rows.append([p.stem,t,float(conf)])
with (R/'05_build/syscg2_ocr_v71.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['asset','text','conf']);w.writerows(rows)
print('FILES',len(files),'HITS',len(rows))
for r in rows:print('\t'.join(map(str,r)))
