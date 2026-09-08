from pathlib import Path
from PIL import Image
import numpy as np,easyocr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/parts2_sparse';rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for p in sorted(D.glob('*.png')):
 im=Image.open(p).convert('RGBA');vars=[]
 for bgc in [(0,0,0,255),(255,255,255,255)]:
  bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(im);vars.append(np.array(bg.convert('RGB')))
 a=np.array(im)[:,:,3];vars+=[np.stack([a,a,a],axis=2),np.stack([255-a]*3,axis=2)]
 print('\n###',p.stem,im.size)
 seen=set()
 for arr in vars:
  for box,t,c in rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.6,text_threshold=.3,low_text=.08,link_threshold=.15):
   if c>=.3 and len(t.strip())>=2 and t not in seen: seen.add(t);print(f'{c:.3f}\t{t}')
