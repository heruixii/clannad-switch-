from pathlib import Path
from PIL import Image
import numpy as np,easyocr,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; D=R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'; O=R/'05_build/config_focus_png'; O.mkdir(exist_ok=True)
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for name in ['CONFIG_BG','CONFIG_BG_EN','CONFIG_TAB','CONFIG_TAB_EN','CONFIG_PARTS','CONFIG_PV_BG']:
 p=D/name; out=O/(name+'.png'); subprocess.run([str(EXE),'export',str(p),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(out).convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); a=np.array(bg.convert('RGB'))
 print('\n###',name,im.size)
 for box,text,conf in rd.readtext(a,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.7,text_threshold=.25,low_text=.08,link_threshold=.15):
  if conf>=.15: print(f'{conf:.3f}\t{text}')
