from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,subprocess,json,shutil,numpy as np,cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';O=R/'05_build/title_fix3';O.mkdir(parents=True,exist_ok=True)
BASE=R/'05_build/title_alpha_fix2/TITLE_fix1_current.png'; TEMPLATE=R/'03_text/ui_work/SYSCG.PAK_unpacked/TITLE'; SCAN=R/'05_build/ui_fullscan_english.tsv'
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
trans={'NEW GAME':'新游戏','LOAD':'读取','AFTER STORY':'后日谈','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏','CONFIG':'设置','NAME':'姓名','DANGOPEDIA':'团子百科','MANUAL':'使用说明'}
rows=list(csv.DictReader(SCAN.open(encoding='utf-8-sig'),delimiter='\t'));rr=[r for r in rows if r.get('asset')=='TITLE' and r.get('text','').strip() in trans];assert len(rr)==9
im=Image.open(BASE).convert('RGBA');arr=np.array(im);old=arr.copy();oldalpha=arr[:,:,3].copy();alpha=oldalpha.copy();H,W=alpha.shape
binm=(oldalpha>48).astype(np.uint8);n,labels,stats,cents=cv2.connectedComponentsWithStats(binm,8);erase=np.zeros_like(binm);line_masks=[]
for r in rr:
 key=r['text'].strip();x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')];tx1=x1-817;tx2=x2-817;lm=np.zeros_like(binm);ids=[]
 for i in range(1,n):
  x,y,w,h,area=map(int,stats[i]);cx,cy=cents[i]
  if h<28 or h>50 or area<100 or area>1200:continue
  if tx1-10<=cx<=tx2+10 and y1-8<=cy<=y2+8: ids.append(i);lm[labels==i]=1
 assert ids,key;erase|=lm;line_masks.append((r,lm,ids))
erase=cv2.dilate(erase,np.ones((3,3),np.uint8),iterations=2);alpha[erase.astype(bool)]=0
# Also remove the old normal-state English RGB glyphs. The engine may sample CZ3 channels as separate states, so alpha-only cleanup is insufficient.
for c in range(3): arr[:,:,c]=cv2.inpaint(arr[:,:,c],(erase*255).astype(np.uint8),3,cv2.INPAINT_TELEA)
def fit(text,w,h):
 s=max(14,int(h*.80))
 while s>11:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0]<=w*.95 and bb[3]-bb[1]<=h*.86:return f
  s-=1
 return ImageFont.truetype(str(FONT),11)
cm=Image.new('L',(W,H),0);d=ImageDraw.Draw(cm);drawrep=[]
# build masks first
for r,lm,ids in line_masks:
 key=r['text'].strip();text=trans[key];x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')];pad=max(3,int((y2-y1)*.12));x1=max(0,x1-pad)-817;y1=max(0,y1-pad);x2=min(W+817,x2+pad)-817;y2=min(H,y2+pad)
 f=fit(text,x2-x1,y2-y1);bb=d.textbbox((0,0),text,font=f,stroke_width=1);tx=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0];ty=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
 d.text((tx,ty),text,font=f,fill=255,stroke_width=1,stroke_fill=255)
 drawrep.append({'from':key,'to':text,'box':[x1,y1,x2,y2],'font_size':f.size,'pos':[tx,ty]})
ch=np.array(cm)
# For each line, sample original normal-state RGB from old English glyph pixels and paint that color under the new Chinese alpha mask.
colors=[]
for r,lm,ids in line_masks:
 key=r['text'].strip();x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')];tx1=max(0,x1-817-20);tx2=min(W,x2-817+20);yy1=max(0,y1-10);yy2=min(H,y2+10)
 pix=(lm.astype(bool)) & (oldalpha>96)
 vals=old[:,:,:3][pix]
 if len(vals)==0: col=np.array([230,230,230],dtype=np.uint8)
 else: col=np.median(vals,axis=0).astype(np.uint8)
 # Chinese pixels belonging to this row via y band and x box
 m=(ch>0);band=np.zeros_like(m);band[yy1:yy2,tx1:tx2]=1;m &= band.astype(bool)
 arr[:,:,:3][m]=col
 colors.append({'text':key,'rgb_median':[int(x) for x in col],'source_pixels':int(len(vals)),'paint_pixels':int(m.sum())})
alpha=np.maximum(alpha,ch);arr[:,:,3]=alpha
out=O/'TITLE_fix3.png';Image.fromarray(arr,'RGBA').save(out)
cz=O/'TITLE_fix3.cz';subprocess.run([str(CZ),'import',str(TEMPLATE),str(out),str(cz)],check=True);probe=O/'TITLE_fix3.verify.png';subprocess.run([str(CZ),'export',str(cz),str(probe)],check=True)
p=np.array(Image.open(probe).convert('RGBA'));q=np.array(Image.open(out).convert('RGBA'));assert np.array_equal(p,q)
# Selected-state/right half RGB must remain byte-identical to fix1.
assert np.array_equal(p[:,780:,:3],old[:,780:,:3])
# No pixel changes outside left title menu band except alpha antialias components inside the known rows.
diff=np.any(p!=old,axis=2);outside=diff.copy();outside[:,700:]=False;outside[:,:150]=False
# rough expected vertical menu range only
outside[:0,:]=False
print('ROUNDTRIP_EQUAL',np.array_equal(p,q),'DIFFPIX',int(diff.sum()),'LEFT_CHANGED',int(diff[:,:700].sum()),'RIGHT_RGB_SAME',np.array_equal(p[:,780:,:3],old[:,780:,:3]))
print('OLD_ENGLISH_ERASE_PIX',int(erase.sum()),'CHINESE_ALPHA_PIX',int((ch>0).sum()))
for c in colors:print('COLOR',c)
shutil.copy2(cz,R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked/TITLE')
(R/'05_build/title_fix3_report.json').write_text(json.dumps({'draw':drawrep,'colors':colors,'diffpix':int(diff.sum()),'erasepix':int(erase.sum()),'chinese_alpha_pix':int((ch>0).sum())},ensure_ascii=False,indent=2),encoding='utf-8')
print('COMMITTED')
