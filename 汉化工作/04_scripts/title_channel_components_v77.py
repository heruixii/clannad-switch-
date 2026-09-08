from pathlib import Path
from PIL import Image
import numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_state_probe')
for fn in ['TITLE.png','TITLE_MASK.png','TITLE_WHITE.png']:
 im=np.array(Image.open(R/fn).convert('RGBA'))
 print('\n##',fn,im.shape)
 for ci,ch in enumerate('RGBA'):
  a=im[:,:,ci]
  # rows/cols with variance or nonzero relative to mode
  vals,cnt=np.unique(a,return_counts=True); mode=vals[cnt.argmax()]
  d=np.abs(a.astype(np.int16)-int(mode))
  mask=d>8
  rs=mask.sum(1); cs=mask.sum(0)
  # contiguous row spans with >=1% width active
  thr=max(2,int(mask.shape[1]*.01)); on=rs>=thr; spans=[];s=None
  for i,v in enumerate(on):
   if v and s is None:s=i
   if s is not None and (not v or i==len(on)-1):
    e=i if not v else i+1
    if e-s>=2:spans.append((s,e,int(rs[s:e].max()),int(rs[s:e].sum())))
    s=None
  print(ch,'mode',int(mode),'ext',int(a.min()),int(a.max()),'rowspans',spans[:40])
