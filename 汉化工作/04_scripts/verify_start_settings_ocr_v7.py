from pathlib import Path
from PIL import Image
import numpy as np,easyocr,subprocess,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; OUT=R/'05_build/start_settings_verify_png'; OUT.mkdir(exist_ok=True)
assets=[('SYSCG','TITLE'),('SYSCG','MN_EX_BG01'),('SYSCG','MN_EX_BG01_EN'),('SYSCG','MN_EX_BG03'),('SYSCG','MN_EX_BG03_EN'),('SYSCG','NAME'),('PARTS','CONFIG_BG'),('PARTS','CONFIG_BG_EN'),('PARTS','CONFIG_TAB'),('PARTS','CONFIG_TAB_EN'),('PARTS','SYSTEM_ICON'),('PARTS','SYSTEM_ICON_EN'),('PARTS','CL_DP_TITLE'),('PARTS','PS_BUTTON_CHIP')]
roots={'SYSCG':R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked','PARTS':R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'}
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False); rep={}; bad=[]
for pak,name in assets:
 src=roots[pak]/name; out=OUT/f'{pak}__{name}.png'; subprocess.run([str(EXE),'export',str(src),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(out).convert('RGBA'); bg=Image.new('RGBA',im.size,(255,255,255,255)); bg.alpha_composite(im); arr=np.array(bg.convert('RGB'))
 hits=[]
 for box,text,conf in rd.readtext(arr,detail=1,paragraph=False,canvas_size=4000,mag_ratio=1.4,text_threshold=.35,low_text=.12,link_threshold=.2):
  if conf>=.45 and sum(c.isalpha() for c in text)>=3:hits.append((text,float(conf)))
 rep[f'{pak}/{name}']=hits
 # Only these old UI words are failures; copyright/brands/music aren't.
 for t,c in hits:
  if re.search(r'(?i)\b(new game|load|after story|cg mode|music mode|config|name|dangopedia|manual|configuration|basic|button1|button2|touch|text1|text2|sound|voice|language|start)\b',t): bad.append((pak,name,t,c))
 print(pak,name,hits[:20])
(R/'05_build/start_settings_ocr_verify.json').write_text(json.dumps({'assets':rep,'bad':bad},ensure_ascii=False,indent=2),encoding='utf-8')
print('BAD',len(bad),bad)
raise SystemExit(1 if bad else 0)
