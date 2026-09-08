from pathlib import Path
from PIL import Image
import easyocr,numpy as np,json,re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\config_layers_fix4_probe');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for fn in ['orig_CONFIG_BG_EN.png','orig_CONFIG_TAB_EN.png']:
 im=np.array(Image.open(D/fn).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=3200,mag_ratio=2.0,text_threshold=.2,low_text=.05,link_threshold=.1,width_ths=.4)
 print('\n###',fn)
 for box,t,c in res:
  if c<.12:continue
  xs=[p[0] for p in box];ys=[p[1] for p in box]
  print(repr(t),round(float(c),3),[round(min(xs),1),round(min(ys),1),round(max(xs),1),round(max(ys),1)])
