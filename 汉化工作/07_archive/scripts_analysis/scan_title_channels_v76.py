from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr,csv,shutil
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/title_state_probe'; O=R/'05_build/title_channel_probe_v76';shutil.rmtree(O,ignore_errors=True);O.mkdir(parents=True)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False); rows=[]
for p in sorted(D.glob('TITLE*.png')):
 im=Image.open(p).convert('RGBA')
 print('\n',p.name,'size',im.size,'extrema',im.getextrema())
 for ci,ch in enumerate('RGBA'):
  plane=im.getchannel(ch)
  if plane.getextrema()[0]==plane.getextrema()[1]:continue
  # both normal and inverted grayscale; OCR handles one but do both once
  for inv in [0,1]:
   g=ImageOps.invert(plane) if inv else plane
   out=O/f'{p.stem}_{ch}{"I" if inv else ""}.png';g.save(out)
   a=np.array(g.convert('RGB'))
   try:res=rd.readtext(a,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.35,low_text=.12,link_threshold=.18)
   except Exception:res=[]
   for box,text,conf in res:
    t=text.strip(); letters=sum(c.isalpha() for c in t)
    if conf>=.30 and letters>=3:
     rows.append([p.name,ch,inv,t,float(conf)])
     print('HIT',ch,inv,repr(t),round(conf,3))
with (R/'05_build/title_channel_ocr_v76.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['asset','channel','invert','text','conf']);w.writerows(rows)
print('\nTOTAL',len(rows))
