from PIL import Image
from pathlib import Path
import numpy as np,cv2,easyocr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/title_state_probe';rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for name in ['TITLE_WHITE','TITLE_MASK']:
 a=np.array(Image.open(D/(name+'.png')).convert('RGBA'));rgb=a[:,:,:3];alpha=a[:,:,3]
 # un-premultiply-ish composites and enhanced variants
 variants={}
 g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);variants['gray']=g;variants['gray_inv']=255-g
 # alpha-weighted luma and RGB channel ranges
 variants['alpha']=alpha;variants['alpha_inv']=255-alpha
 for i,ch in enumerate('RGB'):variants[ch]=rgb[:,:,i];variants[ch+'_inv']=255-rgb[:,:,i]
 # local contrast
 clahe=cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8));variants['clahe']=clahe.apply(g);variants['clahe_inv']=255-variants['clahe']
 print('\n###',name,a.shape)
 for vn,v in variants.items():
  # resize if small details
  try:r=rd.readtext(v,detail=1,paragraph=False,canvas_size=4000,mag_ratio=2.0,text_threshold=.25,low_text=.05,link_threshold=.12)
  except Exception:r=[]
  hits=[(t,float(c),box) for box,t,c in r if c>=.20 and len(t.strip())>=2]
  if hits:
   print('VAR',vn,'hits',len(hits))
   for t,c,b in hits[:60]:print(f'{c:.3f}\t{t}\t{b}')
