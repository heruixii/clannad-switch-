from pathlib import Path
from PIL import Image
import numpy as np,easyocr,re,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\parts2_fix2')
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
terms=['configuration','basic','button','touch','text1','text2','sound','voice','screen']
report={};bad=[]
for n in ['CONFIG_BG_CHS.verify.png','CONFIG_TAB_CHS.verify.png']:
 im=Image.open(D/n).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);arr=np.array(bg.convert('RGB'))
 hits=[]
 for box,t,c in rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=2.0,text_threshold=.25,low_text=.05,link_threshold=.12):
  s=t.strip(); low=re.sub(r'[^a-z0-9]','',s.lower())
  if c>=.18 and s:hits.append({'text':s,'confidence':float(c)})
  if c>=.18 and any(term in low for term in terms):bad.append((n,s,float(c)))
 report[n]=hits
print(json.dumps({'bad':bad,'ocr':report},ensure_ascii=False,indent=2));(D/'parts2_ocr_verify.json').write_text(json.dumps({'bad':bad,'ocr':report},ensure_ascii=False,indent=2),encoding='utf-8')
raise SystemExit(1 if bad else 0)
