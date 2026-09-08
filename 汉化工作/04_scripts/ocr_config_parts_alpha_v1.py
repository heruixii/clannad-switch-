from pathlib import Path
from PIL import Image
import numpy as np,easyocr,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); exe=R/'tools/LuckSystem/tools/cztool/cztool.exe'; D=R/'05_build/config_alpha_probe'; D.mkdir(parents=True,exist_ok=True)
sources={
 'orig_CONFIG_PARTS':R/'03_text/ui_work/PARTS.PAK_unpacked/CONFIG_PARTS',
 'final_CONFIG_PARTS':R/'05_build/ui_packages_v1/PARTS.PAK_unpacked/CONFIG_PARTS',
 'orig_CONFIG_BG_EN':R/'03_text/ui_work/PARTS.PAK_unpacked/CONFIG_BG_EN',
 'final_CONFIG_BG_EN':R/'05_build/ui_packages_v1/PARTS.PAK_unpacked/CONFIG_BG_EN',
}
for n,src in sources.items():
 out=D/(n+'.png'); subprocess.run([str(exe),'export',str(src),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for p in sorted(D.glob('*.png')):
 im=Image.open(p).convert('RGBA')
 variants=[]
 for bgv in [0,255]:
  bg=Image.new('RGBA',im.size,(bgv,bgv,bgv,255)); bg.alpha_composite(im); variants.append((f'bg{bgv}',bg.convert('RGB')))
 # alpha as grayscale to reveal glyph-shaped sprites
 a=im.getchannel('A').convert('RGB'); variants.append(('alpha',a))
 print('\n###',p.stem,im.size,'alpha_bbox',im.getchannel('A').getbbox())
 for tag,v in variants:
  arr=np.array(v.resize((v.width*2,v.height*2),Image.Resampling.LANCZOS))
  try:r=rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.0,text_threshold=.3,low_text=.1,link_threshold=.15)
  except Exception:r=[]
  good=[]
  for box,text,conf in r:
   if conf>=.08 and any(c.isalpha() for c in text):good.append((conf,text,min(x for x,y in box)/2,min(y for x,y in box)/2,max(x for x,y in box)/2,max(y for x,y in box)/2))
  print(' ',tag,'rows',len(good))
  for q in sorted(good,key=lambda x:(x[3],x[2]))[:100]:print('  ',f'{q[0]:.3f}',q[1],tuple(round(x,1) for x in q[2:]))
