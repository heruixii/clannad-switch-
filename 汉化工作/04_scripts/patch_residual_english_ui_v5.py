from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,numpy as np,cv2,shutil,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SRC=R/'05_build/ui_png_zh_v4'; OUT=R/'05_build/ui_png_zh_v5'; ORIG=R/'05_build/ui_png_en'; RES=R/'03_text/ui_work/ui_residual_en_v3.tsv'; TAB=R/'03_text/ui_work/ui_ocr_zh_v3.tsv'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; CZROOT=R/'05_build/ui_cz_v3'
if OUT.exists():shutil.rmtree(OUT)
shutil.copytree(SRC,OUT)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
with RES.open('r',encoding='utf-8-sig',newline='') as f: rr=list(csv.DictReader(f,delimiter='\t'))
with TAB.open('r',encoding='utf-8-sig',newline='') as f: tr=list(csv.DictReader(f,delimiter='\t'))
# reset SYSTEM_ICON from original and redraw only trusted rows
trusted=[r for r in tr if r['asset']=='SYSTEM_ICON_EN' and r['render']=='1' and r['text']!='I0=']
def fit(text,w,h):
 s=max(10,int(h*.75))
 while s>9:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0]<=max(100,w*1.35) and bb[3]-bb[1]<=h*1.2:return f
  s-=1
 return ImageFont.truetype(str(FONT),9)
def edit_box(im,x1,y1,x2,y2,text=None):
 arr=np.array(im.convert('RGBA'));x1=max(0,int(x1));y1=max(0,int(y1));x2=min(im.width,int(x2));y2=min(im.height,int(y2));
 if x2<=x1 or y2<=y1:return im
 region=arr[y1:y2,x1:x2];trans=float((region[:,:,3]<40).mean())
 if trans>.25:arr[y1:y2,x1:x2,3]=0
 else:
  rgb=arr[:,:,:3].copy();mask=np.zeros((im.height,im.width),np.uint8);mask[y1:y2,x1:x2]=255;arr[:,:,:3]=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA)
 im=Image.fromarray(arr,'RGBA')
 if text:
  d=ImageDraw.Draw(im);fo=fit(text,x2-x1,y2-y1);crop=np.array(im)[y1:y2,x1:x2,:3];lum=float(crop.mean()) if crop.size else 128;fill=(20,20,20,255) if lum>145 else (255,255,255,255);stroke=(255,255,255,220) if lum>145 else (0,0,0,220);d.text((x1,y1),text,font=fo,fill=fill,stroke_width=1,stroke_fill=stroke)
 return im
sys=Image.open(ORIG/'SYSTEM_ICON_EN.png').convert('RGBA')
for r in trusted:
 sys=edit_box(sys,float(r['x1'])-5,float(r['y1'])-3,float(r['x2'])+5,float(r['y2'])+3,r['final_zh'])
# second Title row was missed in original table; use residual coordinates
for r in rr:
 if r['asset']=='SYSTEM_ICON_EN' and r['text']=='Title':sys=edit_box(sys,float(r['x1'])-5,float(r['y1'])-3,float(r['x2'])+5,float(r['y2'])+3,'标题画面')
sys.save(OUT/'SYSTEM_ICON_EN.png')
# genuine residuals: clear them; draw only when label needs an explicit replacement
clear_pairs={
 ('EN_HELP3','window'),('EN_MANUAL03','page 13'),('EN_MANUAL04','page 13'),('EN_MANUAL05','ktg and hold'),('EN_MANUAL06','page 11'),('EN_MANUAL06','window'),('EN_MANUAL06','page 15'),('EN_MANUAL06','page 13'),('EN_MANUAL09','you read'),('EN_MANUAL09','screen:'),('EN_MANUAL09','tt'),('EN_MANUAL10','t box'),('EN_MANUAL10','up button:'),('EN_MANUAL10','Menu Or'),('EN_MANUAL17','Of'),('EN_MANUAL25','going')
}
draw_pairs={
 ('EN_MANUAL19','hold A Button'):'按住A键',('EN_MANUAL22','Wait Time Per'):'每字符等待时间',('EN_MANUAL22','Character'):'',('EN_MANUAL23','End source'):'音源',('NAME_EN','{rst Name'):'名',('NAME_EN','tast Name'):'姓'
}
changed={'SYSTEM_ICON_EN'}
for r in rr:
 key=(r['asset'],r['text'])
 if key not in clear_pairs and key not in draw_pairs:continue
 p=OUT/(r['asset']+'.png'); im=Image.open(p).convert('RGBA'); text=draw_pairs.get(key,None)
 im=edit_box(im,float(r['x1'])-8,float(r['y1'])-5,float(r['x2'])+8,float(r['y2'])+5,text if text else None);im.save(p);changed.add(r['asset'])
# reimport changed non-link assets
srcdirs={'SYSCG':R/'03_text/ui_work/SYSCG.PAK_unpacked','PARTS':R/'03_text/ui_work/PARTS.PAK_unpacked','MANUAL':R/'03_text/switch_work/paks/MANUAL.PAK_unpacked'}
for a in sorted(changed):
 pak=None;orig=None
 for k,d in srcdirs.items():
  q=d/a
  if q.exists():pak=k;orig=q;break
 if not orig:raise SystemExit('no source '+a)
 subprocess.run([str(EXE),'import',str(orig),str(OUT/(a+'.png')),str(CZROOT/pak/a)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print('PATCHED',pak,a)
print('CHANGED',len(changed))
