from PIL import Image
from pathlib import Path
import numpy as np,easyocr,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/parts2_sparse';rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for n in ['CONFIG_BG_EN','CONFIG_TAB_EN']:
 im=Image.open(D/(n+'.png')).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);arr=np.array(bg.convert('RGB'))
 print('\n###',n,im.size)
 rs=rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=2.5,text_threshold=.22,low_text=.04,link_threshold=.10)
 for box,t,c in rs:
  if c>=.15:
   xs=[int(p[0]) for p in box];ys=[int(p[1]) for p in box]
   print(json.dumps({'text':t,'conf':round(float(c),4),'box':[min(xs),min(ys),max(xs),max(ys)]},ensure_ascii=False))
