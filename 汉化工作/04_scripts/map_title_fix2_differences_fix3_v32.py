from pathlib import Path
from PIL import Image
import numpy as np,cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');o=np.array(Image.open(R/'05_build/title_state_probe/TITLE.png').convert('RGBA'));c=np.array(Image.open(R/'05_build/title_fix3_probe.png').convert('RGBA'))
for chan,name in [((0,1,2),'RGB'),((3,),'A'),((0,1,2,3),'RGBA')]:
 d=np.any(o[:,:,chan]!=c[:,:,chan],axis=2) if len(chan)>1 else o[:,:,chan[0]]!=c[:,:,chan[0]]
 ys,xs=np.where(d);print(name,'diffpix',int(d.sum()),'bbox',None if not len(xs) else (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)))
 # components of diff mask >=20 px
 n,lab,stats,cent=cv2.connectedComponentsWithStats(d.astype(np.uint8),8); comps=[]
 for i in range(1,n):
  x,y,w,h,a=map(int,stats[i]);
  if a>=20:comps.append((a,x,y,w,h))
 print(' top comps',sorted(comps,reverse=True)[:40])
# per menu y band: diff x ranges
bands=[('NEW',0,80),('LOAD',55,150),('AFTER',120,220),('CG',190,290),('MUSIC',255,360),('CONFIG',325,430),('NAME',395,500),('DANGO',465,565),('MANUAL',535,635)]
for nm,y1,y2 in bands:
 d=np.any(o[y1:y2,:,:3]!=c[y1:y2,:,:3],axis=2);ys,xs=np.where(d)
 print(nm,'RGBdiff',int(d.sum()),'xrange',None if not len(xs) else (int(xs.min()),int(xs.max()+1)))
