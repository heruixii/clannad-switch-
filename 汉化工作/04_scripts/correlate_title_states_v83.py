from pathlib import Path
from PIL import Image
import csv,numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); orig=np.array(Image.open(R/'05_build/title_state_probe/TITLE.png').convert('RGBA')); fix=np.array(Image.open(R/'05_build/title_alpha_fix2/TITLE_fix1_current.png').convert('RGBA'))
rows=list(csv.DictReader((R/'05_build/ui_fullscan_english.tsv').open(encoding='utf-8-sig'),delimiter='\t'));want={'NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL'}
for r in [x for x in rows if x.get('asset')=='TITLE' and x.get('text','').strip() in want]:
 t=r['text'].strip();x1,y1,x2,y2=[int(float(r[k])) for k in ('x1','y1','x2','y2')]; pad=4;sx1=max(0,x1-pad);sx2=min(orig.shape[1],x2+pad);sy1=max(0,y1-pad);sy2=min(orig.shape[0],y2+pad);tx1=sx1-817;tx2=sx2-817
 A=orig[sy1:sy2,tx1:tx2,3].astype(float).ravel()
 print('\n',t,'A stats',A.min(),A.max(),A.mean())
 for ci,ch in enumerate('RGB'):
  X=orig[sy1:sy2,sx1:sx2,ci].astype(float).ravel()
  for inv in [False,True]:
   Y=255-X if inv else X
   c=np.corrcoef(A,Y)[0,1]
   print(ch,'inv' if inv else 'dir','corr',round(float(c),4))
