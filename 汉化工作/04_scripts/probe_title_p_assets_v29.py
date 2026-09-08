from pathlib import Path
from PIL import Image
import numpy as np,easyocr,cv2,json,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/title_state_probe'; SRC=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
# ensure all 13 + effect exported
for n in [f'TITLE_P_{i:02d}' for i in range(1,14)]+['TITLE_P_EFFECT']:
 q=D/(n+'.png')
 if not q.exists(): subprocess.run([str(EXE),'export',str(SRC/n),str(q)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
report={}
for p in sorted(D.glob('TITLE_P_*.png')):
 im=Image.open(p).convert('RGBA'); a=np.array(im);alpha=a[:,:,3]
 ys,xs=np.where(alpha>0);bbox=None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 variants=[]
 for bgc in [(0,0,0,255),(255,255,255,255),(128,128,128,255)]:
  bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(im);variants.append(np.array(bg.convert('RGB')))
 # alpha and inverse
 variants += [np.stack([alpha]*3,axis=2),np.stack([255-alpha]*3,axis=2)]
 hits=[]
 for vi,arr in enumerate(variants):
  # aggressively upscale tiny assets
  mag=max(2.0,min(6.0,600/max(1,im.height)))
  try:rs=rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=mag,text_threshold=.18,low_text=.03,link_threshold=.08)
  except Exception:rs=[]
  for box,t,c in rs:
   if c>=.12 and len(t.strip())>=2:hits.append({'variant':vi,'text':t.strip(),'confidence':round(float(c),4)})
 report[p.stem]={'size':im.size,'alpha_bbox':bbox,'alpha_nonzero':int((alpha>0).sum()),'hits':hits}
 print('\n###',p.stem,'size',im.size,'bbox',bbox,'nz',int((alpha>0).sum()))
 for h in hits[:60]:print(h)
(R/'05_build/title_state_probe/title_p_probe_v29.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
