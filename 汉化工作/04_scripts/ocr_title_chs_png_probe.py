from pathlib import Path
from PIL import Image
import numpy as np,easyocr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); p=R/'05_build/start_settings_fix_png/TITLE_chs.png'; rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False); im=np.array(Image.open(p).convert('RGB')); print([(t,float(c)) for b,t,c in rd.readtext(im,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.4) if c>.4])
