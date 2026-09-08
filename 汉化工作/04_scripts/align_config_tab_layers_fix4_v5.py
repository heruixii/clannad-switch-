from PIL import Image
from pathlib import Path
import numpy as np,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\config_layers_fix4_probe')
a=np.array(Image.open(D/'orig_CONFIG_BG_EN.png').convert('RGBA'))[:80]
b=np.array(Image.open(D/'orig_CONFIG_TAB_EN.png').convert('RGBA'))
# compare shifts of TAB relative to BG top crop using edge/difference masks between EN/base, which isolate text
abase=np.array(Image.open(D/'orig_CONFIG_BG.png').convert('RGBA'))[:80]
bbase=np.array(Image.open(D/'orig_CONFIG_TAB.png').convert('RGBA'))
ma=np.max(np.abs(a.astype(np.int16)-abase.astype(np.int16)),axis=2)>4
mb=np.max(np.abs(b.astype(np.int16)-bbase.astype(np.int16)),axis=2)>4
rep=[]
for dy in range(-10,11):
 for dx in range(-10,11):
  y1=max(0,dy);y2=min(80,80+dy);yb1=max(0,-dy);yb2=min(80,80-dy)
  x1=max(0,dx);x2=min(1920,1920+dx);xb1=max(0,-dx);xb2=min(1920,1920-dx)
  A=ma[y1:y2,x1:x2];B=mb[yb1:yb2,xb1:xb2]
  inter=(A&B).sum();union=(A|B).sum();iou=inter/union if union else 0
  rep.append((iou,dx,dy,int(inter),int(union)))
rep.sort(reverse=True)
print('TOP20')
for z in rep[:20]:print(z)
print('maskpix bg',int(ma.sum()),'tab',int(mb.sum()))
