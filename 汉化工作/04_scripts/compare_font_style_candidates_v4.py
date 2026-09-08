from pathlib import Path
from PIL import Image,ImageFont
from fontTools.ttLib import TTCollection,TTFont
import struct, numpy as np, json, os, math
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
INFO=R/'03_text/switch_work/paks/FONT.PAK_unpacked/info32'
AT=R/'05_build/font_style_probe'
# parse mapping
b=INFO.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0);cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6;pos=head+cnt*3
idx=['\0']*cnt
for cp in range(65536):
 i=struct.unpack_from('<H',b,pos+cp*2)[0]
 if i<cnt and (i!=0 or cp==32): idx[i]=chr(cp)
lookup={c:i for i,c in enumerate(idx) if c!='\0'}
chars=[c for c in '日本学校人生時間風春子山中大小上下左右年月男女先生文字心手目口力水木火土金空雨花川白黒青赤家道新長高低前後東西南北' if c in lookup]
print('chars', ''.join(chars), 'n',len(chars),'fs',fs,'bs',bs)
# normalize crop to 64x64, preserve aspect, center
def norm(a):
 ys,xs=np.where(a>8)
 if len(xs)==0:return None
 c=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
 im=Image.fromarray(c,'L')
 w,h=im.size; scale=min(56/w,56/h); nw=max(1,round(w*scale));nh=max(1,round(h*scale)); im=im.resize((nw,nh),Image.Resampling.LANCZOS)
 out=Image.new('L',(64,64),0); out.paste(im,((64-nw)//2,(64-nh)//2)); return np.array(out,dtype=np.float32)/255
orig={}
for fn in ['ゴシック32','モダン32','明朝32','太丸ゴシック32','丸ゴシック32']:
 im=np.array(Image.open(AT/(fn+'.png')).convert('RGBA'))[:,:,3]
 d={}
 for c in chars:
  i=lookup[c]; x=i%100;y=i//100; cell=im[y*bs:(y+1)*bs,x*bs:(x+1)*bs]; d[c]=norm(cell)
 orig[fn]=d
# candidate font sources
cand_paths=[
 r'C:\Windows\Fonts\NotoSansSC-VF.ttf',r'C:\Windows\Fonts\NotoSerifSC-VF.ttf',r'C:\Windows\Fonts\msyh.ttc',r'C:\Windows\Fonts\msyhbd.ttc',r'C:\Windows\Fonts\msyhl.ttc',r'C:\Windows\Fonts\simhei.ttf',r'C:\Windows\Fonts\simsun.ttc',r'C:\Windows\Fonts\simsunb.ttf',r'C:\Windows\Fonts\Deng.ttf',r'C:\Windows\Fonts\Dengb.ttf',r'C:\Windows\Fonts\Dengl.ttf',r'C:\Windows\Fonts\STXIHEI.TTF',r'C:\Windows\Fonts\STSONG.TTF',r'C:\Windows\Fonts\STZHONGS.TTF',r'C:\Windows\Fonts\SIMYOU.TTF',r'C:\Windows\Fonts\FZYTK.TTF',r'C:\Windows\Fonts\FZSTK.TTF',r'C:\Windows\Fonts\MiSans-Regular.otf',r'C:\Windows\Fonts\msgothic.ttc',r'C:\Windows\Fonts\YuGothM.ttc',r'C:\Windows\Fonts\YuGothR.ttc',r'C:\Windows\Fonts\YuGothB.ttc'
]
def face_count(path):
 try:
  if path.lower().endswith('.ttc'): return len(TTCollection(path).fonts)
 except Exception:pass
 return 1
def family(path,index):
 try:
  tt=TTCollection(path).fonts[index] if path.lower().endswith('.ttc') else TTFont(path)
  vals=[]
  for n in tt['name'].names:
   if n.nameID in (1,2):
    try:s=n.toUnicode()
    except:s=''
    if s and s not in vals:vals.append(s)
  return '/'.join(vals[:4])
 except Exception:return ''
def render(path,index,c):
 try:f=ImageFont.truetype(path,64,index=index)
 except Exception:return None
 # verify non-.notdef using bbox + compare to missing char isn't easy; rely cmap later
 im=Image.new('L',(128,128),0); from PIL import ImageDraw; d=ImageDraw.Draw(im); bb=d.textbbox((0,0),c,font=f,stroke_width=0)
 d.text((64-(bb[2]-bb[0])//2-bb[0],64-(bb[3]-bb[1])//2-bb[1]),c,font=f,fill=255)
 return norm(np.array(im))
def cmap_has(path,index,c):
 try:
  tt=TTCollection(path).fonts[index] if path.lower().endswith('.ttc') else TTFont(path)
  return ord(c) in tt.getBestCmap()
 except:return False
cands=[]
for path in cand_paths:
 if not Path(path).exists():continue
 for fi in range(face_count(path)):
  coverage=sum(cmap_has(path,fi,c) for c in chars)
  # must support at least most common comparison chars
  if coverage < max(10,int(len(chars)*.7)):continue
  cands.append((path,fi,family(path,fi),coverage))
print('candidates',len(cands))
results={}
for family_name,od in orig.items():
 scores=[]
 for path,fi,fam,cov in cands:
  vals=[]
  for c in chars:
   if not cmap_has(path,fi,c):continue
   a=od[c]; q=render(path,fi,c)
   if a is None or q is None:continue
   # Dice-like soft overlap after normalized bbox, plus density diff penalty
   inter=np.minimum(a,q).sum(); union=np.maximum(a,q).sum(); iou=inter/union if union else 0
   mse=np.mean((a-q)**2)
   vals.append((iou, mse))
  if not vals:continue
  score=float(np.mean([v[0] for v in vals])-0.35*np.mean([v[1] for v in vals]))
  scores.append({'score':score,'iou':float(np.mean([v[0] for v in vals])),'mse':float(np.mean([v[1] for v in vals])),'path':path,'index':fi,'family':fam,'n':len(vals)})
 scores.sort(key=lambda x:x['score'],reverse=True);results[family_name]=scores[:12]
 print('\n###',family_name)
 for x in scores[:12]:print(f"{x['score']:.4f}\tiou={x['iou']:.4f}\tmse={x['mse']:.4f}\t{Path(x['path']).name}#{x['index']}\t{x['family']}")
(R/'05_build/font_style_probe/candidate_match_v4.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
