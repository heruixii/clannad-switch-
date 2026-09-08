from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr,subprocess,cv2,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; O=R/'05_build/title_state_probe'; O.mkdir(exist_ok=True)
assets=['TITLE','TITLE_MASK','TITLE_WHITE']+[f'TITLE_P_{i:02d}' for i in range(1,14)]+['TITLE_P_EFFECT']
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False); rep={}
for name in assets:
 p=D/name; out=O/(name+'.png'); subprocess.run([str(EXE),'export',str(p),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(out).convert('RGBA'); a=np.array(im); alpha=a[:,:,3]; rgb=a[:,:,:3]
 variants={
  'black': np.array(Image.new('RGBA',im.size,(0,0,0,255))),
  'white': np.array(Image.new('RGBA',im.size,(255,255,255,255))),
  'alpha': np.stack([alpha,alpha,alpha],axis=2),
  'invalpha': np.stack([255-alpha,255-alpha,255-alpha],axis=2),
 }
 # proper composites
 for bgname,bgc in [('blackcomp',(0,0,0,255)),('whitecomp',(255,255,255,255))]:
  bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(im);variants[bgname]=np.array(bg.convert('RGB'))
 hits=[]
 for vn,arr in variants.items():
  if arr.shape[2]==4: arr=arr[:,:,:3]
  try:r=rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=2.0,text_threshold=.25,low_text=.06,link_threshold=.12)
  except Exception:r=[]
  for box,text,conf in r:
   if conf>=.25 and len(text.strip())>=2:hits.append((vn,text,float(conf)))
 nz=int((alpha>0).sum()); bbox=None
 ys,xs=np.where(alpha>0)
 if len(xs):bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 rep[name]={'size':im.size,'alpha_nonzero':nz,'alpha_bbox':bbox,'alpha_levels':int(len(np.unique(alpha))),'hits':hits}
 print('\n###',name,'size',im.size,'nz',nz,'bbox',bbox,'levels',len(np.unique(alpha)))
 for h in hits[:80]:print(h)
(R/'05_build/title_state_probe/report_v9.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
