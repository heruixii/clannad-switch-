from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import re,subprocess,shutil,datetime,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SRC=R/'03_text/ui_work/OTHCG.PAK_unpacked'; WORK=R/'05_build/othcg_chs_unpacked'; PNG=R/'05_build/othcg_chs_png'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; PC=R/'05_build/pc_ui_zh_png'
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
week='一二三四五六日'
changed=[]
def fit(text,w,h):
 s=max(14,int(h*.72))
 while s>10:
  f=ImageFont.truetype(str(FONT),s); b=f.getbbox(text)
  if b[2]-b[0] <= w*.94 and b[3]-b[1] <= h*.88:return f
  s-=1
 return ImageFont.truetype(str(FONT),10)
def make_text(orig,out,text):
 tmp=PNG/(orig.name+'_date_src.png'); subprocess.run([str(EXE),'export',str(orig),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 im=Image.open(tmp).convert('RGBA'); pix=im.load(); pts=[pix[0,0],pix[im.width-1,0],pix[0,im.height-1],pix[im.width-1,im.height-1]]; bg=tuple(sum(x[i] for x in pts)//4 for i in range(4)); d=ImageDraw.Draw(im); d.rectangle((0,0,im.width,im.height),fill=bg); f=fit(text,im.width,im.height); bb=d.textbbox((0,0),text,font=f,stroke_width=1); x=(im.width-(bb[2]-bb[0]))//2; y=(im.height-(bb[3]-bb[1]))//2-bb[1]; lum=sum(bg[:3])/3; fill=(20,20,20,255) if lum>145 else (255,255,255,255); stroke=(255,255,255,255) if lum>145 else (0,0,0,255); d.text((x,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke); im.save(out)
# C1MMDD_EN / C3MMDD_EN date strips. 2003 calendar matches EN weekday labels.
for p in sorted(SRC.iterdir()):
 m=re.fullmatch(r'C[13](\d\d)(\d\d)_EN',p.name)
 if not m: continue
 mo,da=map(int,m.groups())
 try: dt=datetime.date(2003,mo,da)
 except: continue
 text=f'{mo}月{da}日（周{week[dt.weekday()]}）'; out=PNG/(p.name+'_chs.png'); make_text(p,out,text); subprocess.run([str(EXE),'import',str(p),str(out),str(WORK/p.name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); changed.append((p.name,text))
# _68SNTEN00_EN <- PC SNTEN00 Chinese, scaled to Switch canvas
for name in ['_68SNTEN00_EN']:
 p=SRC/name; q=PC/'SNTEN00.png'
 if p.exists() and q.exists():
  tmp=PNG/(name+'_canvas2.png'); subprocess.run([str(EXE),'export',str(p),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  with Image.open(tmp) as cim, Image.open(q).convert('RGBA') as pim:
   ratio=min(cim.width/pim.width,cim.height/pim.height); nw=max(1,round(pim.width*ratio)); nh=max(1,round(pim.height*ratio)); rs=pim.resize((nw,nh),Image.Resampling.LANCZOS); can=Image.new('RGBA',(cim.width,cim.height),(0,0,0,0)); can.alpha_composite(rs,((cim.width-nw)//2,(cim.height-nh)//2)); out=PNG/(name+'_chs.png'); can.save(out)
  subprocess.run([str(EXE),'import',str(p),str(out),str(WORK/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); changed.append((name,'PC:SNTEN00'))
(R/'05_build/othcg_dates_report.json').write_text(json.dumps(changed,ensure_ascii=False,indent=2),encoding='utf-8')
print('DATE_AND_EXTRA_CHANGED',len(changed)); print(changed[:5],changed[-5:])
