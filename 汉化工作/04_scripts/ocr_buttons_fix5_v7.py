from pathlib import Path
from PIL import Image
import easyocr,numpy as np,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\button_probe_fix5');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
rep={}
for f in sorted(D.glob('*.png')):
 im=np.array(Image.open(f).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.7,text_threshold=.20,low_text=.05,link_threshold=.10,width_ths=.45)
 hits=[]
 for box,t,c in res:
  if c<.12 or sum(ch.isalpha() for ch in t)<2:continue
  xs=[float(p[0]) for p in box];ys=[float(p[1]) for p in box]
  hits.append({'text':t,'confidence':float(c),'box':[min(xs),min(ys),max(xs),max(ys)]})
 rep[f.name]=hits
 print('\n###',f.name)
 for h in hits:print(repr(h['text']),round(h['confidence'],3),[round(x,1) for x in h['box']])
(D.parent/'button_probe_fix5_ocr.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
