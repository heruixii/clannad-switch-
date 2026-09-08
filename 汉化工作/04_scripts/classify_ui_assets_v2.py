from pathlib import Path
from PIL import Image
import csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
D=R/'05_build/ui_png_en'
ocr={}
with (R/'03_text/ui_work/ui_ocr_zh_v1.tsv').open('r',encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f,delimiter='\t'):ocr.setdefault(r['asset'],[]).append(r)
out=[]
for p in sorted(D.glob('*.png')):
    im=Image.open(p).convert('RGBA'); a=im.getchannel('A'); hist=a.histogram(); total=im.width*im.height
    transparent=sum(hist[:250]); fully0=hist[0]; fully255=hist[255]
    rows=ocr.get(p.stem,[]); low=sum(float(r['conf'])<.35 for r in rows)
    out.append([p.stem,im.width,im.height,len(rows),low,fully0/total,transparent/total,fully255/total])
with (R/'03_text/ui_work/ui_asset_classes.tsv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(['asset','width','height','ocr_rows','lowconf','alpha0_ratio','alpha_lt250_ratio','alpha255_ratio']);w.writerows(out)
for r in out: print('\t'.join([str(x) if not isinstance(x,float) else f'{x:.4f}' for x in r]))
