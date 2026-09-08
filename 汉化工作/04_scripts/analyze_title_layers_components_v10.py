from pathlib import Path
from PIL import Image
import numpy as np,cv2,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); O=R/'05_build/title_state_probe'
rep={}
for name in ['TITLE','TITLE_MASK','TITLE_WHITE']:
 im=np.array(Image.open(O/(name+'.png')).convert('RGBA')); a=im[:,:,3]
 print('\n###',name,'size',im.shape[1],im.shape[0],'levels',len(np.unique(a)),'nz',int((a>0).sum()))
 for th in [1,16,64,128,200]:
  m=(a>=th).astype(np.uint8)*255
  n,lab,stats,cent=cv2.connectedComponentsWithStats(m,8)
  comps=[]
  for i in range(1,n):
   x,y,w,h,area=stats[i]
   if area>=20:comps.append((int(area),int(x),int(y),int(w),int(h)))
  comps=sorted(comps,reverse=True)[:40]
  print('th',th,'components',len(comps),'top',comps[:20])
 # row projection bounding intervals where > threshold
 m=a>=32; rp=m.sum(axis=1); intervals=[];on=False
 for y,v in enumerate(rp):
  if v>=10 and not on:st=y;on=True
  if on and (v<10 or y==len(rp)-1):
   en=y if v<10 else y+1
   if en-st>=2: intervals.append((st,en,int(rp[st:en].max()),int(rp[st:en].sum())))
   on=False
 print('row intervals',intervals[:80])
 rep[name]={'row_intervals':intervals}
(R/'05_build/title_state_probe/components_v10.json').write_text(json.dumps(rep,indent=2),encoding='utf-8')
