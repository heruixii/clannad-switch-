from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr,re
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_alpha_fix2\TITLE_final_v86.png');im=Image.open(p).convert('RGBA');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
old=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL']
for label,img in [('alpha',ImageOps.autocontrast(im.getchannel('A')).convert('RGB')),('rgba_black',None)]:
 if img is None:
  bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);img=bg.convert('RGB')
 res=rd.readtext(np.array(img),detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.28,low_text=.08,link_threshold=.15)
 hits=[]
 print('\n##',label)
 for box,t,c in res:
  u=re.sub(r'[^A-Z ]','',t.upper()).strip()
  if c>=.2 and sum(ch.isalpha() for ch in t)>=2:
   print(repr(t),round(float(c),3),box)
   if any(k in u or u in k for k in old if len(u)>=3): hits.append((t,float(c)))
 print('OLD_MENU_HITS',hits)
