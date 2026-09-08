from PIL import Image
from pathlib import Path
import numpy as np,cv2
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_sparse')
for a,b in [('CONFIG_TAB_EN.png','CONFIG_TAB.png'),('CONFIG_BG_EN.png','CONFIG_BG.png')]:
 A=np.array(Image.open(D/a).convert('RGBA'),dtype=np.int16);B=np.array(Image.open(D/b).convert('RGBA'),dtype=np.int16)
 diff=np.max(np.abs(A-B),axis=2);m=(diff>6).astype(np.uint8)*255
 # close text components modestly to word groups
 k=cv2.getStructuringElement(cv2.MORPH_RECT,(11,5));c=cv2.morphologyEx(m,cv2.MORPH_CLOSE,k)
 n,lab,st,cent=cv2.connectedComponentsWithStats(c,8);comps=[]
 for i in range(1,n):
  x,y,w,h,area=st[i]
  if area>=20:comps.append((int(x),int(y),int(w),int(h),int(area)))
 print('\n###',a,'diffpix',int((m>0).sum()),'components')
 for q in sorted(comps,key=lambda z:z[0]):print(q)
