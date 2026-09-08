from pathlib import Path
from PIL import Image
import cv2,numpy as np,csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); A=np.array(Image.open(R/'05_build/title_alpha_fix2/TITLE_fix1_current.png').convert('RGBA'))[:,:,3]
mask=(A>48).astype(np.uint8);n,lab,stats,cents=cv2.connectedComponentsWithStats(mask,8)
rows=list(csv.DictReader((R/'05_build/ui_fullscan_english.tsv').open(encoding='utf-8-sig'),delimiter='\t'));want={'NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL'}
for r in [x for x in rows if x.get('asset')=='TITLE' and x.get('text','').strip() in want]:
 t=r['text'].strip();x1,y1,x2,y2=[int(float(r[k])) for k in ('x1','y1','x2','y2')];x1-=817;x2-=817
 print('\n##',t,'box',x1,y1,x2,y2)
 comps=[]
 for i in range(1,n):
  x,y,w,h,area=stats[i];cx,cy=cents[i]
  ix=max(x,x1);iy=max(y,y1);ix2=min(x+w,x2);iy2=min(y+h,y2)
  if ix<ix2 and iy<iy2:
   inter=(lab[iy:iy2,ix:ix2]==i).sum(); comps.append((i,x,y,w,h,int(area),round(float(cx),1),round(float(cy),1),int(inter)))
 for c in sorted(comps,key=lambda z:z[1]):print(c)
