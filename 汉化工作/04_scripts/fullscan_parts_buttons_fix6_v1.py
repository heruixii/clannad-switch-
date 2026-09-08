from pathlib import Path
from PIL import Image
import subprocess,json,easyocr,numpy as np,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';SRC=R/'05_build/ui_packages_fix5/PARTS.PAK_unpacked';O=R/'05_build/button_fullscan_fix6';O.mkdir(parents=True,exist_ok=True)
# export all PARTS assets likely to contain UI labels based on dimensions/names; OCR every decodable asset but skip huge art where useful
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
rep=[];old=[]
for f in SRC.iterdir():
 if not f.is_file(): continue
 png=O/(f.name+'.png')
 try:
  subprocess.run([str(CZ),'export',str(f),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20)
 except Exception:
  continue
 try:
  im=Image.open(png).convert('RGB')
 except: continue
 w,h=im.size
 # UI-like only: moderate sizes, skip large photos except known BG/icon assets
 if w*h>3000000 and not any(k in f.name.upper() for k in ['SYSTEM','BUTTON','ICON','MENU','SAVE','LOAD','DIALOG','SELECT','WINDOW','DP_']):
  png.unlink(missing_ok=True);continue
 a=np.array(im);res=rd.readtext(a,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.2,low_text=.05,link_threshold=.1,width_ths=.45)
 hits=[]
 for box,t,c in res:
  if c<.18 or sum(ch.isalpha() for ch in t)<2:continue
  u=' '.join(re.sub(r'[^A-Za-z ]',' ',t).upper().split())
  if len(u)<2:continue
  xs=[float(x[0]) for x in box];ys=[float(x[1]) for x in box]
  hits.append({'text':t,'norm':u,'conf':float(c),'box':[min(xs),min(ys),max(xs),max(ys)]})
 if hits:
  rep.append({'asset':f.name,'size':[w,h],'hits':hits})
  print('\n##',f.name,w,h)
  for x in hits:print(repr(x['text']),round(x['conf'],3),x['box'])
(R/'05_build/button_fullscan_fix6.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print('ASSETS_WITH_ENGLISH',len(rep))
