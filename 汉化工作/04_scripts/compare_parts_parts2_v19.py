from PIL import Image
from pathlib import Path
import numpy as np, cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_compare')
def cmp(a,b):
 A=np.array(Image.open(R/a).convert('RGBA'),dtype=np.int16);B=np.array(Image.open(R/b).convert('RGBA'),dtype=np.int16)
 d=np.max(np.abs(A-B),axis=2);m=d>2
 ys,xs=np.where(m)
 box=None if not len(xs) else (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
 return {'shape':A.shape,'diffpix':int(m.sum()),'ratio':float(m.mean()),'bbox':box,'mean_abs':float(np.abs(A-B).mean()),'max':int(np.abs(A-B).max())}
for n in ['CONFIG_BG','CONFIG_BG_EN','CONFIG_TAB','CONFIG_TAB_EN']:
 print('\n',n)
 print('PARTS orig vs PARTS2',cmp(f'PARTS_orig_{n}.png',f'PARTS2_{n}.png'))
 print('PARTS patched vs PARTS2',cmp(f'PARTS_patched_{n}.png',f'PARTS2_{n}.png'))
