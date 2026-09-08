from pathlib import Path
import csv,subprocess,json,re
from PIL import Image
import easyocr,numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';SRC=R/'05_build/othcg_chs_unpacked';O=R/'05_build/othcg_button_probe_fix6';O.mkdir(parents=True,exist_ok=True)
groups=list(csv.DictReader((R/'03_text/ui_work/othcg_groups_v1.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False);targets=['YES','NO','NEXT','BACK','CLOSE','CANCEL','RETURN','DELETE','LATEST','CONTINUE','SAVE','LOAD','OK','CONFIRM','SKIP','JUMP'];rep=[]
for gi,g in enumerate(groups):
 f=SRC/g['representative'];
 if not f.exists():continue
 png=O/(g['group']+'.png')
 try:subprocess.run([str(CZ),'export',str(f),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=20)
 except:continue
 try:im=Image.open(png).convert('RGB')
 except:continue
 if im.width*im.height>4000000:continue
 res=rd.readtext(np.array(im),detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.18,low_text=.04,link_threshold=.1,width_ths=.4)
 hits=[]
 for box,t,c in res:
  if c<.12 or sum(ch.isalpha() for ch in t)<2:continue
  u=''.join(ch for ch in t.upper() if ch.isalpha())
  if any(k in u or (u in k and len(u)>=2) for k in targets):
   xs=[float(p[0]) for p in box];ys=[float(p[1]) for p in box];hits.append({'text':t,'norm':u,'conf':float(c),'box':[min(xs),min(ys),max(xs),max(ys)]})
 if hits:
  row={'group':g['group'],'rep':g['representative'],'frames':int(g['frame_count']),'size':[im.width,im.height],'hits':hits};rep.append(row);print('\n##',g['group'],g['representative'],im.size);[print(repr(x['text']),round(x['conf'],3),x['box']) for x in hits]
(R/'05_build/othcg_button_probe_fix6.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print('GROUPS_WITH_BUTTON_EN',len(rep))
