from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,numpy as np,shutil,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SRC=R/'05_build/ui_png_zh_v3'; ORIG=R/'05_build/ui_png_en'; OUT=R/'05_build/ui_png_zh_v4'; TAB=R/'03_text/ui_work/ui_ocr_zh_v3.tsv'; CZDIR=R/'05_build/ui_cz_v3/MANUAL'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; MAN=R/'03_text/switch_work/paks/MANUAL.PAK_unpacked'
if OUT.exists():shutil.rmtree(OUT)
shutil.copytree(SRC,OUT)
with TAB.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
by={}
for r in rows:
 if '_LINKTO_' in r['asset'] and r['render']=='1' and r['final_zh'].strip():by.setdefault(r['asset'],[]).append(r['final_zh'].strip())
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
def pick_color(im):
 a=np.array(im.convert('RGBA')); pix=a[a[:,:,3]>180]
 if len(pix)==0:return (255,255,255,255)
 # pick median visible original glyph color
 med=np.median(pix,axis=0).astype(int);return tuple(int(x) for x in med)
def fit(text,w,h):
 s=max(10,int(h*.62))
 while s>8:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0] <= w-12 and bb[3]-bb[1] <= h-4:return f
  s-=1
 return ImageFont.truetype(str(FONT),8)
for asset,texts in sorted(by.items()):
 p=ORIG/(asset+'.png'); orig=Image.open(p).convert('RGBA'); text='；'.join(dict.fromkeys(texts))
 base=Image.new('RGBA',orig.size,(0,0,0,0)); f=fit(text,*orig.size); d=ImageDraw.Draw(base);bb=d.textbbox((0,0),text,font=f);x=max(4,(orig.width-(bb[2]-bb[0]))//2);y=max(0,(orig.height-(bb[3]-bb[1]))//2-bb[1]); color=pick_color(orig)
 # binary glyph mask: no antialias palette explosion
 mask=Image.new('L',orig.size,0);md=ImageDraw.Draw(mask);md.text((x,y),text,font=f,fill=255);arr=np.array(mask);arr=np.where(arr>=96,255,0).astype('uint8');mask=Image.fromarray(arr,'L'); layer=Image.new('RGBA',orig.size,color);base.alpha_composite(Image.composite(layer,Image.new('RGBA',orig.size,(0,0,0,0)),mask))
 base.save(OUT/(asset+'.png'))
 subprocess.run([str(EXE),'import',str(MAN/asset),str(OUT/(asset+'.png')),str(CZDIR/asset)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print(asset,orig.size,text,color)
print('LINKS',len(by))
