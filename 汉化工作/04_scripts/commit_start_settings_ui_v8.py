from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,shutil,numpy as np,cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; PNG=R/'05_build/start_settings_fix_png'; TMP=R/'05_build/start_settings_fix_cz'; TMP.mkdir(exist_ok=True)
SY=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'; PA=R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc')] if p.exists())

def commit(root,name,png):
 src=root/name; out=TMP/(name+'.new')
 if out.exists():out.unlink()
 subprocess.run([str(EXE),'import',str(src),str(png),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if not out.exists() or out.stat().st_size<100:raise RuntimeError('bad output '+name)
 # decode once before replacing, to prove the generated CZ is readable
 probe=TMP/(name+'.probe.png'); subprocess.run([str(EXE),'export',str(out),str(probe)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 shutil.move(str(out),str(src)); print('COMMITTED',name,src.stat().st_size)

# Commit the already-rendered corrected PNGs.
for root,name in [(SY,'TITLE'),(SY,'NAME'),(PA,'CL_DP_TITLE'),(PA,'PS_BUTTON_CHIP')]:
 commit(root,name,PNG/(name+'_chs.png'))

# Explicitly remove the one remaining English label from the system menu.
src=PA/'SYSTEM_ICON_EN'; exp=PNG/'SYSTEM_ICON_EN_explicit_src.png'; outpng=PNG/'SYSTEM_ICON_EN_explicit_chs.png'
subprocess.run([str(EXE),'export',str(src),str(exp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
im=Image.open(exp).convert('RGBA'); arr=np.array(im); x1,y1,x2,y2=620,525,925,632
reg=arr[y1:y2,x1:x2]; trans=float((reg[:,:,3]<48).mean())
if trans>.20: arr[y1:y2,x1:x2]=0
else:
 rgb=arr[:,:,:3].copy(); mask=np.zeros((im.height,im.width),np.uint8);mask[y1:y2,x1:x2]=255;arr[:,:,:3]=cv2.inpaint(rgb,mask,4,cv2.INPAINT_TELEA)
im=Image.fromarray(arr,'RGBA'); d=ImageDraw.Draw(im); text='团子百科'; size=56
while size>18:
 f=ImageFont.truetype(str(FONT),size); bb=d.textbbox((0,0),text,font=f,stroke_width=1)
 if bb[2]-bb[0]<(x2-x1)*.9 and bb[3]-bb[1]<(y2-y1)*.8:break
 size-=1
tx=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0];ty=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
a=np.array(im)[y1:y2,x1:x2,:3];lum=float(a.mean()) if a.size else 80;fill=(24,24,24,255) if lum>145 else (255,255,255,255);stroke=(255,255,255,220) if lum>145 else (0,0,0,220)
d.text((tx,ty),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke);im.save(outpng)
commit(PA,'SYSTEM_ICON_EN',outpng);shutil.copy2(PA/'SYSTEM_ICON_EN',PA/'SYSTEM_ICON');print('MIRRORED SYSTEM_ICON')
# Keep base/EN settings branches identical Chinese.
for base,en in [('CONFIG_BG','CONFIG_BG_EN'),('CONFIG_TAB','CONFIG_TAB_EN')]:shutil.copy2(PA/en,PA/base);print('MIRRORED',base)
for base,en in [('MN_EX_BG01','MN_EX_BG01_EN'),('MN_EX_BG03','MN_EX_BG03_EN')]:shutil.copy2(SY/en,SY/base);print('MIRRORED',base)
