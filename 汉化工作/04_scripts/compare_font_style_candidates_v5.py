from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
from fontTools.ttLib import TTCollection,TTFont
import struct,numpy as np,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); INFO=R/'03_text/switch_work/paks/FONT.PAK_unpacked/info32'; AT=R/'05_build/font_style_probe'
b=INFO.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0);cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third;head=8 if third==100 else 6;pos=head+cnt*3
idx=['\0']*cnt
for cp in range(65536):
 i=struct.unpack_from('<H',b,pos+cp*2)[0]
 if i<cnt and (i!=0 or cp==32):idx[i]=chr(cp)
lookup={c:i for i,c in enumerate(idx) if c!='\0'}
chars=[c for c in '日本学校人生時間風春子山中大小左右年月男女文字心手目口水木火金空雨花川白黒青家道新長高前後東西南北' if c in lookup][:28]
print('chars', ''.join(chars), 'n',len(chars),'fs',fs,'bs',bs,flush=True)
def norm(a):
 ys,xs=np.where(a>8)
 if len(xs)==0:return None
 c=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
 im=Image.fromarray(c,'L');w,h=im.size;scale=min(56/w,56/h);nw=max(1,round(w*scale));nh=max(1,round(h*scale));im=im.resize((nw,nh),Image.Resampling.LANCZOS)
 out=Image.new('L',(64,64),0);out.paste(im,((64-nw)//2,(64-nh)//2));return np.asarray(out,dtype=np.float32)/255
orig={}
for fn in ['ゴシック32','モダン32','明朝32','太丸ゴシック32','丸ゴシック32']:
 im=np.asarray(Image.open(AT/(fn+'.png')).convert('RGBA'))[:,:,3];orig[fn]={}
 for c in chars:
  i=lookup[c];x=i%100;y=i//100;orig[fn][c]=norm(im[y*bs:(y+1)*bs,x*bs:(x+1)*bs])
paths=[r'C:\Windows\Fonts\NotoSansSC-VF.ttf',r'C:\Windows\Fonts\NotoSerifSC-VF.ttf',r'C:\Windows\Fonts\msyh.ttc',r'C:\Windows\Fonts\msyhbd.ttc',r'C:\Windows\Fonts\msyhl.ttc',r'C:\Windows\Fonts\simhei.ttf',r'C:\Windows\Fonts\simsun.ttc',r'C:\Windows\Fonts\simsunb.ttf',r'C:\Windows\Fonts\Deng.ttf',r'C:\Windows\Fonts\Dengb.ttf',r'C:\Windows\Fonts\Dengl.ttf',r'C:\Windows\Fonts\STXIHEI.TTF',r'C:\Windows\Fonts\STSONG.TTF',r'C:\Windows\Fonts\STZHONGS.TTF',r'C:\Windows\Fonts\SIMYOU.TTF',r'C:\Windows\Fonts\FZYTK.TTF',r'C:\Windows\Fonts\FZSTK.TTF',r'C:\Windows\Fonts\MiSans-Regular.otf',r'C:\Windows\Fonts\msgothic.ttc',r'C:\Windows\Fonts\YuGothM.ttc',r'C:\Windows\Fonts\YuGothR.ttc',r'C:\Windows\Fonts\YuGothB.ttc']
def names(tt):
 vals=[]
 for n in tt['name'].names:
  if n.nameID in (1,2):
   try:s=n.toUnicode()
   except:s=''
   if s and s not in vals:vals.append(s)
 return '/'.join(vals[:4])
cands=[]
for path in paths:
 if not Path(path).exists():continue
 try:
  fonts=TTCollection(path).fonts if path.lower().endswith('.ttc') else [TTFont(path)]
 except Exception:continue
 for fi,tt in enumerate(fonts):
  cmap=tt.getBestCmap() or {}; cov=sum(ord(c) in cmap for c in chars)
  if cov<18:continue
  try:face=ImageFont.truetype(path,64,index=fi)
  except Exception:continue
  rendered={}
  for c in chars:
   if ord(c) not in cmap:continue
   im=Image.new('L',(128,128),0);d=ImageDraw.Draw(im);bb=d.textbbox((0,0),c,font=face);d.text((64-(bb[2]-bb[0])//2-bb[0],64-(bb[3]-bb[1])//2-bb[1]),c,font=face,fill=255);rendered[c]=norm(np.asarray(im))
  cands.append((path,fi,names(tt),rendered))
print('candidates',len(cands),flush=True)
results={}
for fam,od in orig.items():
 arr=[]
 for path,fi,name,rd in cands:
  vals=[]
  for c,a in od.items():
   q=rd.get(c)
   if q is None:continue
   inter=np.minimum(a,q).sum();union=np.maximum(a,q).sum();iou=inter/union if union else 0;mse=np.mean((a-q)**2);vals.append((iou,mse))
  if not vals:continue
  iou=float(np.mean([v[0] for v in vals]));mse=float(np.mean([v[1] for v in vals]));score=iou-.35*mse
  arr.append({'score':score,'iou':iou,'mse':mse,'path':path,'index':fi,'family':name,'n':len(vals)})
 arr.sort(key=lambda x:x['score'],reverse=True);results[fam]=arr[:10]
 print('\n###',fam,flush=True)
 for x in arr[:10]:print(f"{x['score']:.4f}\tiou={x['iou']:.4f}\tmse={x['mse']:.4f}\t{Path(x['path']).name}#{x['index']}\t{x['family']}",flush=True)
(R/'05_build/font_style_probe/candidate_match_v5.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
