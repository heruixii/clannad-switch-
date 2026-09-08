from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr,re,json
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_fix3\TITLE_fix3.verify.png');im=Image.open(P).convert('RGBA');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
old=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL']
variants=[]
for ch in 'RGBA':variants.append((ch,ImageOps.autocontrast(im.getchannel(ch)).convert('RGB')))
variants.append(('RGBRAW',im.convert('RGB')))
bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);variants.append(('VISIBLE_BLACK',bg.convert('RGB')))
report={};bad=[]
for label,img in variants:
 res=rd.readtext(np.array(img),detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.25,low_text=.07,link_threshold=.15)
 hits=[];alltxt=[]
 for box,t,c in res:
  if c<.18 or sum(ch.isalpha() for ch in t)<2:continue
  u=re.sub(r'[^A-Z ]','',t.upper()).strip();alltxt.append((t,float(c)))
  if len(u)>=3 and any(k in u or u in k for k in old):hits.append((t,float(c)))
 report[label]={'hits':hits,'ocr':alltxt[:80]};bad.extend((label,*x) for x in hits)
 print(label,'OLD_MENU_HITS',hits)
print('TOTAL_BAD',len(bad))
O=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_fix3_ocr_qa.json');O.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if bad:raise SystemExit(2)
