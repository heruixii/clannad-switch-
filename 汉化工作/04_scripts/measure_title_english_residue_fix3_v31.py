from pathlib import Path
from PIL import Image
import numpy as np,cv2,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
orig=np.array(Image.open(R/'05_build/title_state_probe/TITLE.png').convert('RGBA'))
cur=np.array(Image.open(R/'05_build/title_fix3_probe.png').convert('RGBA'))
A=orig[:,:,3]; bm=(A>48).astype(np.uint8);n,lab,stats,cents=cv2.connectedComponentsWithStats(bm,8)
# Select exact English alpha glyph components from known menu band x/y/size; excludes CLANNAD/copyright.
ids=[]
for i in range(1,n):
 x,y,w,h,area=map(int,stats[i]);cx,cy=cents[i]
 if 200<=cx<=620 and 0<=cy<=620 and 28<=h<=50 and 100<=area<=1200:
  ids.append(i)
mask=np.isin(lab,ids).astype(np.uint8)
# Shift to right selected RGB copy.
M=np.float32([[1,0,817],[0,1,0]]);rm=cv2.warpAffine(mask,M,(mask.shape[1],mask.shape[0]),flags=cv2.INTER_NEAREST,borderValue=0).astype(bool)
# include antialias/glow neighborhood
rmd=cv2.dilate(rm.astype(np.uint8),np.ones((5,5),np.uint8),iterations=1).astype(bool)
D=np.abs(cur[:,:,:3].astype(np.int16)-orig[:,:,:3].astype(np.int16));eq=np.all(cur[:,:,:3]==orig[:,:,:3],axis=2);mag=D.max(axis=2)
print('GLYPH_COMPONENTS',len(ids),'maskpix',int(rm.sum()),'dilated',int(rmd.sum()))
for name,m in [('core',rm),('dilated',rmd)]:
 print(name,'unchanged_exact',round(float(eq[m].mean()),4),'changed>5',round(float((mag[m]>5).mean()),4),'changed>30',round(float((mag[m]>30).mean()),4),'mean_diff',round(float(mag[m].mean()),2))
# Per-line based on y centers
bands=[('NEW GAME',0,65),('LOAD',65,135),('AFTER STORY',135,205),('CG MODE',205,275),('MUSIC MODE',275,345),('CONFIG',345,415),('NAME',415,485),('DANGOPEDIA',485,555),('MANUAL',555,625)]
for nm,y1,y2 in bands:
 m=rm.copy();m[:y1]=False;m[y2:]=False
 if m.sum():print(nm,'pix',int(m.sum()),'unchanged',round(float(eq[m].mean()),4),'diff>30',round(float((mag[m]>30).mean()),4),'mean',round(float(mag[m].mean()),2))
# left alpha old English removal check current alpha versus original mask
print('LEFT_ALPHA current>48 on old glyph cores',round(float((cur[:,:,3][mask.astype(bool)]>48).mean()),4),'mean',round(float(cur[:,:,3][mask.astype(bool)].mean()),2))
