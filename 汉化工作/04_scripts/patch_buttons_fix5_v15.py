from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,subprocess,shutil,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';SRC=R/'05_build/ui_packages_fix4/PARTS.PAK_unpacked';O=R/'05_build/button_fix5';O.mkdir(parents=True,exist_ok=True)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())

def export(name):
 png=O/(name+'.src.png');subprocess.run([str(CZ),'export',str(SRC/name),str(png)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);return Image.open(png).convert('RGBA')

def encode(name,im):
 png=O/(name+'.fix5.png');im.save(png);out=O/(name+'.fix5');subprocess.run([str(CZ),'import',str(SRC/name),str(png),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);probe=O/(name+'.verify.png');subprocess.run([str(CZ),'export',str(out),str(probe)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);A=np.array(im);B=np.array(Image.open(probe).convert('RGBA'));print(name,'roundtrip_equal',bool(np.array_equal(A,B)),'diffpix',int(np.any(A!=B,axis=2).sum()),'maxdiff',int(np.abs(A.astype(int)-B.astype(int)).max()));return out,probe
# SKIP icons: remove static English text areas only; preserve left ~45px controller glyph in each 168px state cell.
rep={}
for name in ['SKIP_ICON_00','SKIP_ICON_01']:
 im=export(name);A=np.array(im);mask=np.zeros(A.shape[:2],np.uint8)
 for col in range(4):
  x0=col*168
  for x1,y1,x2,y2 in [(x0+48,0,x0+168,103),(x0+45,130,x0+168,240)]:
   mask[max(0,y1):min(A.shape[0],y2),max(0,x1):min(A.shape[1],x2)]=255
 # inpaint each RGBA channel to reconstruct transparent/background area without touching controller glyph strip
 Oa=A.copy()
 for c in range(4):Oa[:,:,c]=cv2.inpaint(A[:,:,c],mask,4,cv2.INPAINT_TELEA)
 out,probe=encode(name,Image.fromarray(Oa,'RGBA'));rep[name]={'mask_pixels':int((mask>0).sum()),'out':str(out),'probe':str(probe)}
# PS button chip: START is already Chinese in fix4; replace remaining SELECT with 选择.
name='PS_BUTTON_CHIP';im=export(name);A=np.array(im);mask=np.zeros(A.shape[:2],np.uint8);mask[0:34,298:384]=255
Oa=A.copy()
for c in range(4):Oa[:,:,c]=cv2.inpaint(A[:,:,c],mask,3,cv2.INPAINT_TELEA)
im2=Image.fromarray(Oa,'RGBA');d=ImageDraw.Draw(im2);text='选择';box=(298,0,384,34)
size=24
while size>=12:
 f=ImageFont.truetype(str(FONT),size);bb=d.textbbox((0,0),text,font=f,stroke_width=1)
 if bb[2]-bb[0] <= (box[2]-box[0])*.9 and bb[3]-bb[1] <= (box[3]-box[1])*.8:break
 size-=1
reg=np.array(im2)[0:34,298:384,:3];lum=float(reg.mean()) if reg.size else 80;fill=(245,245,245,255) if lum<145 else (25,25,25,255);stroke=(0,0,0,220) if lum<145 else (255,255,255,220);x=box[0]+((box[2]-box[0])-(bb[2]-bb[0]))//2-bb[0];y=box[1]+((box[3]-box[1])-(bb[3]-bb[1]))//2-bb[1];d.text((x,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke)
out,probe=encode(name,im2);rep[name]={'mask_pixels':int((mask>0).sum()),'font_size':size,'pos':[x,y],'out':str(out),'probe':str(probe)}
(O/'button_fix5_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2))
