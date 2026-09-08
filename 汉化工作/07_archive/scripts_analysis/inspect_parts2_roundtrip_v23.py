from PIL import Image
from pathlib import Path
import numpy as np
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_fix2')
A=np.array(Image.open(D/'CONFIG_BG_CHS.png').convert('RGBA'),dtype=np.int16);B=np.array(Image.open(D/'CONFIG_BG_CHS.verify.png').convert('RGBA'),dtype=np.int16)
d=np.abs(A-B);m=np.max(d,axis=2)
print('shape',A.shape,'max',d.max(),'mean',d.mean(),'diff>0',int((m>0).sum()),'diff>1',int((m>1).sum()),'diff>4',int((m>4).sum()),'diff>16',int((m>16).sum()))
ys,xs=np.where(m>4);print('bbox>4',None if not len(xs) else (xs.min(),ys.min(),xs.max()+1,ys.max()+1))
for ch,n in enumerate('RGBA'):print(n,'max',d[:,:,ch].max(),'mean',d[:,:,ch].mean(),'gt4',int((d[:,:,ch]>4).sum()))
