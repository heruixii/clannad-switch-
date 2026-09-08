from pathlib import Path
from PIL import Image
import easyocr,numpy as np,re,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\button_fix5');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
targets=['SKIP','BACK','JUMP','SELECT'];bad=[];rep={}
for fn in ['SKIP_ICON_00.verify.png','SKIP_ICON_01.verify.png','PS_BUTTON_CHIP.verify.png']:
 im=np.array(Image.open(D/fn).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.8,text_threshold=.18,low_text=.04,link_threshold=.10,width_ths=.4)
 hits=[]
 for box,t,c in res:
  if c<.12 or sum(ch.isalpha() for ch in t)<2:continue
  u=re.sub(r'[^A-Z]','',t.upper());hits.append((t,float(c),u))
  if any(k in u or u in k for k in targets if len(u)>=3):bad.append((fn,t,float(c)))
 rep[fn]=hits;print('\n',fn);print('BAD',[x for x in bad if x[0]==fn]);print('OCR',hits[:60])
(D/'button_fix5_ocr_qa.json').write_text(json.dumps({'bad':bad,'ocr':rep},ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL_BAD',len(bad));raise SystemExit(1 if bad else 0)
