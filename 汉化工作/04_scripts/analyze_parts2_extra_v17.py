from PIL import Image
from pathlib import Path
import numpy as np,cv2
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_sparse\EXTRA_64116.png'); a=np.array(Image.open(p).convert('RGBA'));alpha=a[:,:,3];rgb=a[:,:,:3]
print('shape',a.shape,'alpha levels',len(np.unique(alpha)),'nz',int((alpha>0).sum()),'rgb minmax',rgb.min(),rgb.max(),'unique sample',len(np.unique(rgb.reshape(-1,3),axis=0)))
for th in [1,16,64,128,200]:
 m=(alpha>=th).astype(np.uint8)*255;n,lab,stats,cent=cv2.connectedComponentsWithStats(m,8);cs=[]
 for i in range(1,n):
  x,y,w,h,area=stats[i]
  if area>=8:cs.append((int(area),int(x),int(y),int(w),int(h)))
 cs.sort(reverse=True);print('th',th,'count',len(cs),'top',cs[:80])
# row/column projections
for th in [16,64,128]:
 m=alpha>=th
 rp=m.sum(1);cp=m.sum(0)
 print('row peaks',th,sorted([(int(v),i) for i,v in enumerate(rp)],reverse=True)[:20])
 print('col peaks',th,sorted([(int(v),i) for i,v in enumerate(cp)],reverse=True)[:20])
