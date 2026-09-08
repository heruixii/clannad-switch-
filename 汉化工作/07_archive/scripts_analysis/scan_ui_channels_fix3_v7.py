from pathlib import Path
from PIL import Image,ImageOps
import subprocess,shutil,numpy as np,easyocr,csv,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe';O=R/'05_build/ui_fix3_channel_probe';shutil.rmtree(O,ignore_errors=True);O.mkdir(parents=True)
assets=[]
for pak,d,names in [
 ('SYSCG',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked',['TITLE','NAME','NAME_EN','NAMEBASE','NAMEBASE_EN']),
 ('PARTS',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked',['CONFIG_BG','CONFIG_BG_EN','CONFIG_TAB','CONFIG_TAB_EN','CONFIG_PARTS','CONFIG_PV_BG','SYSTEM_ICON','SYSTEM_ICON_EN','N_BUTTON_CHIP','N_BUTTON_CHIP_BLACK','N_BUTTON_CHIP_GRAY','PS_BUTTON_CHIP'])]:
 for n in names:
  src=d/n
  if src.exists():
   out=O/f'{pak}__{n}.png';r=subprocess.run([str(CZ),'export',str(src),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   if r.returncode==0 and out.exists(): assets.append((pak,n,out))
# already-decoded PARTS2 fix2 verify images
for n in ['CONFIG_BG_CHS.verify.png','CONFIG_TAB_CHS.verify.png']:
 p=R/'05_build/parts2_fix2'/n
 if p.exists(): assets.append(('PARTS2',n,p))
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False);rows=[]
for ai,(pak,name,p) in enumerate(assets,1):
 im=Image.open(p).convert('RGBA')
 variants=[]
 for ch in 'RGBA':
  pl=im.getchannel(ch)
  if pl.getextrema()[0]!=pl.getextrema()[1]: variants.append((ch,ImageOps.autocontrast(pl).convert('RGB')))
 # raw RGB ignores alpha, and visible composite
 variants.append(('RGBRAW',im.convert('RGB')))
 bg=Image.new('RGBA',im.size,(0,0,0,255));bg.alpha_composite(im);variants.append(('VIS',bg.convert('RGB')))
 for ch,img in variants:
  a=np.array(img);H,W=a.shape[:2]
  chunks=[]
  if H>1500:
   y=0
   while y<H:
    y2=min(H,y+1100);chunks.append((y,a[y:y2]));
    if y2==H:break
    y=y2-80
  else:chunks=[(0,a)]
  for y0,arr in chunks:
   try:res=rd.readtext(arr,detail=1,paragraph=False,canvas_size=3000,mag_ratio=1.3,text_threshold=.30,low_text=.10,link_threshold=.16)
   except Exception:res=[]
   for box,t,c in res:
    tt=t.strip();letters=sum(x.isalpha() for x in tt)
    if c>=.28 and letters>=2 and len(tt)<=100:
     rows.append([pak,name,ch,tt,float(c),min(x for x,y in box),min(y for x,y in box)+y0,max(x for x,y in box),max(y for x,y in box)+y0])
 print('DONE',ai,'/',len(assets),pak,name,'hits',sum(1 for r in rows if r[0]==pak and r[1]==name),flush=True)
with (R/'05_build/ui_fix3_channel_english.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['pak','asset','channel','text','conf','x1','y1','x2','y2']);w.writerows(rows)
print('\nTOTAL',len(rows))
for r in rows: print('\t'.join(map(str,r[:5])))
