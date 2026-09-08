from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_state_probe');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for fn in ['TITLE_MASK.png','TITLE_WHITE.png']:
 im=Image.open(D/fn).convert('RGBA')
 for ch in 'RGBA':
  plane=im.getchannel(ch)
  if plane.getextrema()[0]==plane.getextrema()[1]:continue
  # high-contrast normalize channel
  a=np.array(ImageOps.autocontrast(plane).convert('RGB'))
  res=rd.readtext(a,detail=1,paragraph=False,canvas_size=3000,mag_ratio=2.0,text_threshold=.30,low_text=.10,link_threshold=.15)
  hits=[]
  for box,t,c in res:
   if c>=.2 and sum(x.isalpha() for x in t)>=2:hits.append((t,float(c),box))
  print('\n',fn,ch,'hits',len(hits))
  for h in hits[:50]:print(h[0],round(h[1],3),h[2])
