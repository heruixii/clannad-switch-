from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,numpy as np,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');SCAN=R/'05_build/ui_fullscan_english.tsv';FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
trans={'NEW GAME':'新游戏','LOAD':'读取','AFTER STORY':'后日谈','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏','CONFIG':'设置','NAME':'姓名','DANGOPEDIA':'团子百科','MANUAL':'使用说明'}
rows=list(csv.DictReader(SCAN.open(encoding='utf-8-sig'),delimiter='\t'));rr=[r for r in rows if r.get('asset')=='TITLE' and r.get('text','').strip() in trans]
W,H=1568,783
def fit(text,w,h):
 s=max(14,int(h*.80))
 while s>11:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0]<=w*.95 and bb[3]-bb[1]<=h*.86:return f
  s-=1
 return ImageFont.truetype(str(FONT),11)
def make(shift):
 cm=Image.new('L',(W,H),0);d=ImageDraw.Draw(cm);rep=[]
 for r in rr:
  key=r['text'].strip();text=trans[key];x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')];pad=max(3,int((y2-y1)*.12));x1=max(0,x1-pad)+shift;y1=max(0,y1-pad);x2=min(W-shift if shift<0 else W,x2+pad)+shift;y2=min(H,y2+pad)
  f=fit(text,x2-x1,y2-y1);bb=d.textbbox((0,0),text,font=f,stroke_width=1);tx=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0];ty=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
  d.text((tx,ty),text,font=f,fill=255,stroke_width=1,stroke_fill=255);rep.append((key,f.size,tx,ty,x1,y1,x2,y2))
 return np.array(cm),rep
right,rrp=make(0);left,lrp=make(-817)
# compare right shifted into left coordinates exactly
shifted=np.zeros_like(right); shifted[:,0:W-817]=right[:,817:W]
# only compare menu rectangles where right source exists
u=(left>0)|(shifted>0);inter=((left>0)&(shifted>0)).sum();union=u.sum()
print('MASK_EQUAL',bool(np.array_equal(left,shifted)),'IOU',float(inter/union if union else 1),'XOR',int(((left>0)^(shifted>0)).sum()))
for a,b in zip(rrp,lrp):print('R',a,'L',b,'delta',(a[2]-b[2],a[3]-b[3]))
