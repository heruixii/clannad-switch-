from pathlib import Path
import easyocr,numpy as np,json
from PIL import Image
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\config_layers_fix4_probe');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
for f in sorted(D.glob('*.png')):
 im=np.array(Image.open(f).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.4,text_threshold=.25,low_text=.08,link_threshold=.15)
 hits=[(t,round(float(c),3)) for box,t,c in res if c>=.18 and sum(ch.isalpha() for ch in t)>=2]
 print(f.name,hits[:80])
