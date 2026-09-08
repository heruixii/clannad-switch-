from pathlib import Path
import easyocr,csv,json,time
from PIL import Image
import numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
D=R/'05_build/ui_png_en'
OUT=R/'03_text/ui_work/ui_ocr_en.tsv'
reader=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
files=sorted(D.glob('*.png'))
rows=[]
for i,p in enumerate(files,1):
    im=Image.open(p).convert('RGB'); arr=np.array(im); W,H=im.size
    # Tall music-title atlas is segmented vertically to retain OCR scale.
    chunks=[]
    if H>2500:
        step=1200; overlap=80
        y=0
        while y<H:
            y2=min(H,y+step); chunks.append((y,y2,arr[y:y2]));
            if y2==H: break
            y=y2-overlap
    else: chunks=[(0,H,arr)]
    seen=set()
    t=time.time()
    for y0,y1,a in chunks:
        out=reader.readtext(a,detail=1,paragraph=False,canvas_size=3500,mag_ratio=1.0,text_threshold=.5,low_text=.25,link_threshold=.25)
        for box,text,conf in out:
            pts=[(float(x),float(y)+y0) for x,y in box]
            x1=min(x for x,y in pts); y1b=min(y for x,y in pts); x2=max(x for x,y in pts); y2=max(y for x,y in pts)
            key=(round(x1/4),round(y1b/4),text.strip().lower())
            if key in seen: continue
            seen.add(key)
            rows.append([p.stem,text.strip(),f'{float(conf):.6f}',f'{x1:.1f}',f'{y1b:.1f}',f'{x2:.1f}',f'{y2:.1f}',W,H])
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['asset','text','conf','x1','y1','x2','y2','width','height']);w.writerows(rows)
    if i%5==0 or i==len(files):
        print(f'OCR {i}/{len(files)} rows={len(rows)} last={p.name} sec={time.time()-t:.2f}',flush=True)
print('DONE',len(files),len(rows))
