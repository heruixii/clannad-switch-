from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,easyocr,re,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_fix3_probe.png');im=Image.open(p).convert('RGBA');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
old=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL']
rows=[]
# raw RGB channels ignore alpha entirely; alpha separately; also RGB composite with forced opaque alpha
for ch in 'RGBA':
    g=ImageOps.autocontrast(im.getchannel(ch)).convert('RGB')
    res=rd.readtext(np.array(g),detail=1,paragraph=False,canvas_size=3600,mag_ratio=1.8,text_threshold=.25,low_text=.07,link_threshold=.14)
    print('\n## CHANNEL',ch)
    for box,t,c in res:
        if c>=.18 and sum(x.isalpha() for x in t)>=2:
            u=re.sub(r'[^A-Z ]','',t.upper()).strip(); hit=any(k in u or (len(u)>=3 and u in k) for k in old)
            print(repr(t),round(float(c),3),'OLD' if hit else '',box); rows.append((ch,t,float(c),hit,box))
# raw RGB image, force alpha=255
rgb=im.convert('RGB');res=rd.readtext(np.array(rgb),detail=1,paragraph=False,canvas_size=3600,mag_ratio=1.8,text_threshold=.25,low_text=.07,link_threshold=.14)
print('\n## RAW_RGB')
for box,t,c in res:
    if c>=.18 and sum(x.isalpha() for x in t)>=2:
        u=re.sub(r'[^A-Z ]','',t.upper()).strip(); hit=any(k in u or (len(u)>=3 and u in k) for k in old)
        print(repr(t),round(float(c),3),'OLD' if hit else '',box)
