from pathlib import Path
import easyocr,numpy as np
from PIL import Image
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/menu_probe_png'; rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for p in sorted(D.glob('*.png')):
 im=np.array(Image.open(p).convert('RGB'))
 try:r=rd.readtext(im,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.4,text_threshold=.4,low_text=.2,link_threshold=.25)
 except Exception:r=[]
 print('\n###',p.stem,Image.open(p).size)
 for box,text,conf in sorted(r,key=lambda x:(min(y for x,y in x[0]),min(x for x,y in x[0]))):
  if conf>=.12:print(f'{conf:.3f}\t{text}')
