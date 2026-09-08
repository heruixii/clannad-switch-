from pathlib import Path
from PIL import Image
import numpy as np,csv,re,time,easyocr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/ui_png_zh_v3'; OUT=R/'03_text/ui_work/ui_residual_en_v3.tsv'
reader=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
rows=[]; files=sorted(D.glob('*.png'))
for i,p in enumerate(files,1):
    im=Image.open(p).convert('RGB');arr=np.array(im); H=im.height
    chunks=[]
    if H>2500:
        y=0
        while y<H:
            y2=min(H,y+1200);chunks.append((y,arr[y:y2]));
            if y2==H:break
            y=y2-80
    else:chunks=[(0,arr)]
    for y0,a in chunks:
        try:o=reader.readtext(a,detail=1,paragraph=False,canvas_size=3500,mag_ratio=1.0,text_threshold=.55,low_text=.3,link_threshold=.3)
        except Exception:o=[]
        for box,text,conf in o:
            if float(conf)<.50:continue
            if not re.search(r'[A-Za-z]{2,}',text):continue
            pts=[(float(x),float(y)+y0) for x,y in box]; rows.append([p.stem,text,float(conf),min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)])
    if i%10==0 or i==len(files):print('SCAN',i,'/',len(files),'rows',len(rows),flush=True)
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter='\t');w.writerow(['asset','text','conf','x1','y1','x2','y2']);w.writerows(rows)
print('DONE',len(rows))
