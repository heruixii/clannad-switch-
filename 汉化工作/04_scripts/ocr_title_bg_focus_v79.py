from pathlib import Path
from PIL import Image,ImageOps,ImageEnhance
import numpy as np,easyocr,cv2
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_state_probe');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
terms='NEW GAME LOAD AFTER STORY CG MODE MUSIC MODE CONFIG NAME DANGOPEDIA MANUAL'.lower().split()
for fn in ['TITLE01.png','TITLE02.png']:
 im=Image.open(D/fn).convert('RGB'); W,H=im.size
 # scan right 60%, where switch title menu is expected; include full if needed
 crops=[('right',im.crop((700,0,W,H))),('full',im)]
 for cname,c in crops:
  g=np.array(c.convert('L'))
  variants=[('gray',g),('clahe',cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8)).apply(g))]
  variants += [('otsu',cv2.threshold(v,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]) for _,v in variants[:2]]
  print('\n##',fn,cname)
  for vn,a in variants:
   res=rd.readtext(np.stack([a]*3,-1),detail=1,paragraph=False,canvas_size=3600,mag_ratio=1.5,text_threshold=.25,low_text=.08,link_threshold=.15)
   hits=[]
   for box,t,conf in res:
    if conf>=.15 and sum(ch.isalpha() for ch in t)>=2:hits.append((t,float(conf),box))
   print(vn,'hits',len(hits))
   for h in hits[:80]: print(' ',repr(h[0]),round(h[1],3),h[2])
