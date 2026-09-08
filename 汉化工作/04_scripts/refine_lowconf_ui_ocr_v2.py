from pathlib import Path
import csv,re,time
from PIL import Image,ImageEnhance,ImageOps
import numpy as np
import easyocr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=R/'03_text/ui_work/ui_ocr_zh_v1.tsv'; IMG=R/'05_build/ui_png_en'; OUT=R/'03_text/ui_work/ui_ocr_refined_v2.tsv'
with SRC.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
reader=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
cache={}; improved=0
for i,r in enumerate(rows,1):
    old=float(r['conf']); r['refined_text']=r['normalized_en']; r['refined_conf']=r['conf']; r['refine_used']='0'
    if old>=.40: continue
    p=IMG/(r['asset']+'.png'); im=Image.open(p).convert('RGB')
    x1=max(0,int(float(r['x1']))-10); y1=max(0,int(float(r['y1']))-8); x2=min(im.width,int(float(r['x2']))+10); y2=min(im.height,int(float(r['y2']))+8)
    if x2<=x1 or y2<=y1: continue
    cr=im.crop((x1,y1,x2,y2)).resize(((x2-x1)*3,(y2-y1)*3),Image.Resampling.LANCZOS)
    # boost contrast but preserve colored text
    cr=ImageEnhance.Contrast(cr).enhance(1.5)
    try: out=reader.readtext(np.array(cr),detail=1,paragraph=False,canvas_size=2000,mag_ratio=1.0,text_threshold=.35,low_text=.15,link_threshold=.2)
    except Exception: out=[]
    if out:
        # prefer highest-confidence nontrivial candidate, or concatenate spatial order
        cand=sorted(out,key=lambda z:min(pt[0] for pt in z[0]))
        text=' '.join(z[1] for z in cand if z[1].strip()).strip(); conf=sum(float(z[2]) for z in cand)/len(cand)
        if text and conf>old+0.08:
            r['refined_text']=text; r['refined_conf']=f'{conf:.6f}'; r['refine_used']='1'; improved+=1
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
    fields=list(rows[0].keys())+['refined_text','refined_conf','refine_used']; w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
print('TOTAL',len(rows),'LOW',sum(float(r['conf'])<.4 for r in rows),'IMPROVED',improved)
for r in rows:
    if r['refine_used']=='1': print(r['asset'],'|',r['text'],'[',r['conf'],'] =>',r['refined_text'],'[',r['refined_conf'],']')
