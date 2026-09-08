from pathlib import Path
import easyocr,json,time
from PIL import Image
import numpy as np
imgs=[Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\ui_png_en\CONFIG_TAB_EN.png'),Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\ui_png_en\SYSTEM_ICON_EN.png'),Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\ui_png_en\EN_MANUAL01.png')]
r=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for p in imgs:
 arr=np.array(Image.open(p).convert('RGB'))
 t=time.time(); out=r.readtext(arr,detail=1,paragraph=False,canvas_size=3500,mag_ratio=1.0,text_threshold=.55,low_text=.3,link_threshold=.3)
 print('===',p.name,'n',len(out),'sec',round(time.time()-t,2))
 for box,text,conf in out:
  print(json.dumps({'text':text,'conf':round(float(conf),4),'box':[[int(x),int(y)] for x,y in box]},ensure_ascii=False))
