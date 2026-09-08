from pathlib import Path
from PIL import Image
import struct,statistics,collections
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
INFO=R/'03_text/switch_work/paks/FONT.PAK_unpacked/info24'
PNG=R/'05_build/font_baseline_probe.png'
b=INFO.read_bytes(); fs,bs,third=struct.unpack_from('<HHH',b,0); cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third; head=8 if third==100 else 6; pos=head+cnt*3
idx=['\0']*cnt
for cp in range(65536):
 i=struct.unpack_from('<H',b,pos+cp*2)[0]
 if i<cnt and (i!=0 or cp==32): idx[i]=chr(cp)
im=Image.open(PNG).convert('RGBA'); A=im.getchannel('A')
def bbox_cell(i):
 x=i%100; y=i//100; x0=x*bs;y0=y*bs; box=A.crop((x0,y0,x0+bs,y0+bs)).getbbox()
 if not box:return None
 return box
rows=[]
for i,ch in enumerate(idx):
 if ch=='\0':continue
 cp=ord(ch)
 if 0x3000<=cp<=0x9fff or 0xff00<=cp<=0xffef:
  box=bbox_cell(i)
  if box: rows.append((i,ch,*box))
print('fs bs cnt',fs,bs,cnt,'cjk boxes',len(rows))
tops=[r[3] for r in rows]; bots=[r[5] for r in rows]; heights=[r[5]-r[3] for r in rows]
for name,v in [('top',tops),('bottom',bots),('height',heights)]:
 print(name,'min',min(v),'p10',statistics.quantiles(v,n=10)[0],'median',statistics.median(v),'mode',collections.Counter(v).most_common(10),'max',max(v))
print('sample common JP chars')
for ch in '日本語私町人学校風子春原渚朋也設定開始終了文字':
 try:i=idx.index(ch)
 except ValueError:continue
 print(ch,i,bbox_cell(i))
