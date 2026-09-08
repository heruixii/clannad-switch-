from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,subprocess,struct,hashlib,json,shutil
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';O=R/'05_build/config_fix4';O.mkdir(parents=True,exist_ok=True)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
P2=R/'05_build/parts2_sparse';P1=R/'03_text/ui_work/PARTS.PAK_unpacked'

def erase_lang(en,base):
 A=np.array(en.convert('RGBA'));B=np.array(base.convert('RGBA'));diff=np.max(np.abs(A.astype(np.int16)-B.astype(np.int16)),axis=2);mask=(diff>4).astype(np.uint8)*255;mask=cv2.dilate(mask,np.ones((5,5),np.uint8),iterations=1);out=A.copy()
 for c in range(4):out[:,:,c]=cv2.inpaint(A[:,:,c],mask,3,cv2.INPAINT_TELEA)
 return Image.fromarray(out,'RGBA'),mask

def fit(text,w,h,max_size=34):
 s=min(max_size,int(h*.72))
 while s>=14:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0]<=w*.88 and bb[3]-bb[1]<=h*.76:return f
  s-=1
 return ImageFont.truetype(str(FONT),14)

def draw_center(im,box,text,max_size=34):
 x1,y1,x2,y2=box;d=ImageDraw.Draw(im);f=fit(text,x2-x1,y2-y1,max_size);bb=d.textbbox((0,0),text,font=f,stroke_width=1);x=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0];y=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
 arr=np.array(im.convert('RGBA'));reg=arr[max(0,y1):min(im.height,y2),max(0,x1):min(im.width,x2),:3];lum=float(reg.mean()) if reg.size else 80;fill=(245,245,245,255) if lum<145 else (25,25,25,255);stroke=(0,0,0,210) if lum<145 else (255,255,255,210);d.text((x,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke);return {'text':text,'box':box,'font':f.size,'pos':[x,y],'fill':fill}
# PARTS2 authoritative static UI. Clean all original language pixels first.
bg_en=Image.open(P2/'CONFIG_BG_EN.png').convert('RGBA');bg_base=Image.open(P2/'CONFIG_BG.png').convert('RGBA');tab_en=Image.open(P2/'CONFIG_TAB_EN.png').convert('RGBA');tab_base=Image.open(P2/'CONFIG_TAB.png').convert('RGBA');bg,bgm=erase_lang(bg_en,bg_base);tab,tabm=erase_lang(tab_en,tab_base)
# title only in BG
rep={'bg_mask_pixels':int((bgm>0).sum()),'tab_mask_pixels':int((tabm>0).sum()),'draw':[]}
rep['draw'].append({'layer':'BG','item':draw_center(bg,(18,0,380,120),'设置',58)})
# canonical tab masks: draw in BG at stock y≈13..94; copy same rendered pixels to TAB shifted -14px (stock median relation).
labels=['基本','按键1','按键2','触摸','文本1','文本2','音效','语音','画面'];left,right=333,1890;step=(right-left)/9.0
canvas=Image.new('RGBA',bg.size,(0,0,0,0));cd=ImageDraw.Draw(canvas)
for i,t in enumerate(labels):
 x1=round(left+i*step);x2=round(left+(i+1)*step);box=(x1+4,13,x2-4,94);f=fit(t,box[2]-box[0],box[3]-box[1],34);bb=cd.textbbox((0,0),t,font=f,stroke_width=1);x=box[0]+((box[2]-box[0])-(bb[2]-bb[0]))//2-bb[0];y=box[1]+((box[3]-box[1])-(bb[3]-bb[1]))//2-bb[1];cd.text((x,y),t,font=f,fill=(245,245,245,255),stroke_width=1,stroke_fill=(0,0,0,210));rep['draw'].append({'layer':'canonical','text':t,'font':f.size,'pos':[x,y],'box':box})
# composite canonical into BG
bg.alpha_composite(canvas)
# exact same glyph pixels shifted -14 into TAB; crop top 80
ca=np.array(canvas);ta=np.array(tab);src=ca[14:94,:,:]; # source y14..93 -> target y0..79
# alpha composite src over tab pixel-exact
srcim=Image.fromarray(src,'RGBA');tab.alpha_composite(srcim,(0,0))
# save/encode from untouched PARTS2 EN templates
for stem,im in [('CONFIG_BG',bg),('CONFIG_TAB',tab)]:
 png=O/f'PARTS2_{stem}_CHS.png';im.save(png);cz=O/f'PARTS2_{stem}_CHS';subprocess.run([str(CZ),'import',str(P2/(stem+'_EN')),str(png),str(cz)],check=True);probe=O/f'PARTS2_{stem}_CHS.verify.png';subprocess.run([str(CZ),'export',str(cz),str(probe)],check=True);A=np.array(im).astype(np.int16);B=np.array(Image.open(probe).convert('RGBA')).astype(np.int16);d=np.max(np.abs(A-B),axis=2);allowed=np.zeros(d.shape,np.uint8);allowed[:130,:1900]=1 if stem=='CONFIG_BG' else 0;allowed[:80,300:1920]=1;outside=int(((d>1)&(allowed==0)).sum());assert outside==0,(stem,outside,int(d.max()))
# PARTS1 neutral config assets: erase language differences and add no text. Encode same neutral image to base+EN ids.
neutral={}
for stem in ['CONFIG_BG','CONFIG_TAB']:
 tmpen=O/f'_p1_{stem}_en.png';tmpbase=O/f'_p1_{stem}_base.png';subprocess.run([str(CZ),'export',str(P1/(stem+'_EN')),str(tmpen)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);subprocess.run([str(CZ),'export',str(P1/stem),str(tmpbase)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);en=Image.open(tmpen).convert('RGBA');base=Image.open(tmpbase).convert('RGBA');clean,mask=erase_lang(en,base);png=O/f'PARTS1_{stem}_NEUTRAL.png';clean.save(png);neutral[stem]={'mask_pixels':int((mask>0).sum())}
 for suffix in ['', '_EN']:
  out=O/f'PARTS1_{stem}{suffix}_NEUTRAL';subprocess.run([str(CZ),'import',str(P1/(stem+suffix)),str(png),str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  probe=O/f'PARTS1_{stem}{suffix}_NEUTRAL.verify.png';subprocess.run([str(CZ),'export',str(out),str(probe)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);A=np.array(clean).astype(np.int16);B=np.array(Image.open(probe).convert('RGBA')).astype(np.int16);d=np.max(np.abs(A-B),axis=2);allowed=(mask>0);outside=int(((d>1)&(~allowed)).sum());assert outside==0,(stem,suffix,outside,int(d.max()))
rep['neutral_parts1']=neutral
(O/'config_fix4_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2));print('DONE')
