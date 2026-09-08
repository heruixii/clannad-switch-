from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_final_alpha_probe_v80.png');im=Image.open(p).convert('RGBA');print('SIZE',im.size,'EXT',im.getextrema());rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for ch in ['R','G','B','A']:
 a=ImageOps.autocontrast(im.getchannel(ch));res=rd.readtext(np.array(a.convert('RGB')),detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.3,low_text=.1,link_threshold=.15)
 print('\nCHANNEL',ch)
 for box,t,c in res:
  if c>=.25 and sum(x.isalpha() for x in t)>=2: print(repr(t),round(float(c),3),box)
