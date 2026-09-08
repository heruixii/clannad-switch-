from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_sparse');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for fn in ['CONFIG_BG.png','CONFIG_BG_EN.png','CONFIG_TAB.png','CONFIG_TAB_EN.png']:
 im=Image.open(D/fn).convert('RGBA');print('\n###',fn,im.size)
 variants=[]
 for ch in 'RGBA':
  pl=im.getchannel(ch)
  if pl.getextrema()[0]!=pl.getextrema()[1]:variants.append((ch,ImageOps.autocontrast(pl).convert('RGB')))
 variants.append(('RGB',im.convert('RGB')))
 for vn,v in variants:
  res=rd.readtext(np.array(v),detail=1,paragraph=False,canvas_size=3800,mag_ratio=1.5,text_threshold=.25,low_text=.07,link_threshold=.14)
  hits=[]
  for box,t,c in res:
   if c>=.18 and sum(x.isalpha() for x in t)>=2:hits.append((t,float(c),box))
  if hits:
   print(' ',vn)
   for t,c,b in hits: print('   ',repr(t),round(c,3),b)
