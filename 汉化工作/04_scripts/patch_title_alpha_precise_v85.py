from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,subprocess,json,shutil,numpy as np,cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';O=R/'05_build/title_alpha_fix2';O.mkdir(parents=True,exist_ok=True)
BASE=O/'TITLE_fix1_current.png'; TEMPLATE=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked/TITLE'; SCAN=R/'05_build/ui_fullscan_english.tsv'
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
trans={'NEW GAME':'新游戏','LOAD':'读取','AFTER STORY':'后日谈','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏','CONFIG':'设置','NAME':'姓名','DANGOPEDIA':'团子百科','MANUAL':'使用说明'}
rows=list(csv.DictReader(SCAN.open(encoding='utf-8-sig'),delimiter='\t'));rr=[r for r in rows if r.get('asset')=='TITLE' and r.get('text','').strip() in trans];assert len(rr)==9
im=Image.open(BASE).convert('RGBA');arr=np.array(im);oldalpha=arr[:,:,3].copy(); alpha=oldalpha.copy(); H,W=alpha.shape
# Find high-confidence English letter components from old alpha.
binm=(oldalpha>48).astype(np.uint8);n,labels,stats,cents=cv2.connectedComponentsWithStats(binm,8);erase=np.zeros_like(binm)
removed=[]
for r in rr:
 key=r['text'].strip();x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')]; tx1=x1-817;tx2=x2-817
 ids=[]
 for i in range(1,n):
  x,y,w,h,area=map(int,stats[i]); cx,cy=cents[i]
  if h<28 or h>50 or area<100 or area>1200: continue
  # component center within OCR-derived target band/box (small margin)
  if tx1-10 <= cx <= tx2+10 and y1-8 <= cy <= y2+8:
   ids.append(i); erase[labels==i]=1
 assert ids, key
 removed.append({'text':key,'component_ids':ids})
# Remove antialias fringe around the identified English glyphs only.
erase=cv2.dilate(erase,np.ones((3,3),np.uint8),iterations=2)
alpha[erase.astype(bool)]=0

def fit(text,w,h):
 s=max(14,int(h*.80))
 while s>11:
  f=ImageFont.truetype(str(FONT),s);bb=f.getbbox(text)
  if bb[2]-bb[0] <= w*.95 and bb[3]-bb[1] <= h*.86:return f
  s-=1
 return ImageFont.truetype(str(FONT),11)
# Draw Chinese into a separate alpha mask using the same geometry/rules as selected-state patch v6.
cm=Image.new('L',(W,H),0);d=ImageDraw.Draw(cm);drawrep=[]
for r in rr:
 key=r['text'].strip();text=trans[key];x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')]
 pad=max(3,int((y2-y1)*.12)); x1=max(0,x1-pad)-817; y1=max(0,y1-pad); x2=min(W+817,x2+pad)-817; y2=min(H,y2+pad)
 f=fit(text,x2-x1,y2-y1);bb=d.textbbox((0,0),text,font=f,stroke_width=1);tx=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0];ty=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
 d.text((tx,ty),text,font=f,fill=255,stroke_width=1,stroke_fill=255)
 drawrep.append({'from':key,'to':text,'box':[x1,y1,x2,y2],'font_size':f.size,'pos':[tx,ty]})
ch=np.array(cm);alpha=np.maximum(alpha,ch);arr[:,:,3]=alpha
out=O/'TITLE_fix2_precise.png';Image.fromarray(arr,'RGBA').save(out)
tmp=O/'TITLE_fix2_precise.cz';subprocess.run([str(CZ),'import',str(TEMPLATE),str(out),str(tmp)],check=True)
probe=O/'TITLE_fix2_precise_roundtrip.png';subprocess.run([str(CZ),'export',str(tmp),str(probe)],check=True)
p=np.array(Image.open(probe).convert('RGBA'));q=np.array(Image.open(out).convert('RGBA'))
print('ROUNDTRIP_EQUAL',bool(np.array_equal(p,q)),'DIFFPIX',int(np.any(p!=q,axis=2).sum()),'MAXDIFF',int(np.abs(p.astype(int)-q.astype(int)).max()))
print('RGB_SAME_FIX1',bool(np.array_equal(p[:,:,:3],np.array(im)[:,:,:3])))
print('ALPHA_CHANGED_PIX',int((p[:,:,3]!=oldalpha).sum()),'ERASE_PIX',int(erase.sum()),'CHINESE_PIX',int((ch>0).sum()))
for z in removed:print('REMOVED',z)
for z in drawrep:print('DRAW',z)
assert np.array_equal(p,q);assert np.array_equal(p[:,:,:3],np.array(im)[:,:,:3])
shutil.copy2(tmp,TEMPLATE)
(R/'05_build/title_alpha_fix2_precise_report.json').write_text(json.dumps({'removed':removed,'draw':drawrep},ensure_ascii=False,indent=2),encoding='utf-8')
print('COMMITTED',TEMPLATE)
