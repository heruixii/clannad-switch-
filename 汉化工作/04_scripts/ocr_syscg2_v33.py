from pathlib import Path
from PIL import Image
import numpy as np,easyocr,json,re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\syscg2_probe');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
rep={};targets=[]
for p in sorted(D.glob('ID_*.png'),key=lambda p:int(p.stem.split('_')[1])):
 im=Image.open(p).convert('RGBA'); bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);arr=np.array(bg.convert('RGB'))
 hits=[]
 try:rs=rd.readtext(arr,detail=1,paragraph=False,canvas_size=2200,mag_ratio=1.3,text_threshold=.25,low_text=.05,link_threshold=.12)
 except Exception:rs=[]
 for box,t,c in rs:
  if c>=.18 and len(t.strip())>=2:hits.append({'text':t.strip(),'confidence':round(float(c),3)})
 rep[p.stem]=hits
 if hits:
  print(p.stem,hits,flush=True)
  txt=' '.join(x['text'] for x in hits).lower()
  if any(k in txt for k in ['new','game','load','after','story','mode','config','name','dango','manual']):targets.append((p.stem,hits))
(D/'ocr_v33.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print('TARGETS',json.dumps(targets,ensure_ascii=False),flush=True)
