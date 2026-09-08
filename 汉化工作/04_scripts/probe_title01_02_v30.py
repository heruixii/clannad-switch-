from pathlib import Path
from PIL import Image
import numpy as np,easyocr,subprocess,json,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/title_state_probe';SRC=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked';EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
for n in ['TITLE01','TITLE02']:
 q=D/(n+'.png');subprocess.run([str(EXE),'export',str(SRC/n),str(q)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False);rep={}
for n in ['TITLE01','TITLE02']:
 im=Image.open(D/(n+'.png')).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);arr=np.array(bg.convert('RGB'))
 hits=[]
 for box,t,c in rd.readtext(arr,detail=1,paragraph=False,canvas_size=5000,mag_ratio=1.5,text_threshold=.2,low_text=.04,link_threshold=.1):
  if c>=.15 and len(t.strip())>=2:
   xs=[int(x[0]) for x in box];ys=[int(x[1]) for x in box]; hits.append({'text':t.strip(),'confidence':float(c),'box':[min(xs),min(ys),max(xs),max(ys)]})
 rep[n]={'size':im.size,'hits':hits};print('\n###',n,im.size);[print(x) for x in hits]
(D/'title01_02_ocr_v30.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
