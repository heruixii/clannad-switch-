from pathlib import Path
from PIL import Image
import easyocr,numpy as np,re,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\button_global_probe_fix6');rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False)
keys=['SAVE','LOAD','BACK','CLOSE','YES','NO','OK','CANCEL','RETURN','START','SELECT','JUMP','SKIP','MENU','AUTO','QUICK','SYSTEM','VOICE','CONFIG','SETTING','DEFAULT','EXIT','TITLE','LOG','HIDE','SCREEN','WINDOW','TEXT','SOUND','TOUCH','BUTTON','FORWARD','REWIND']
rep={};bad=[]
for f in sorted(D.glob('*.png')):
 im=np.array(Image.open(f).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=4096,mag_ratio=1.7,text_threshold=.18,low_text=.04,link_threshold=.10,width_ths=.45)
 hits=[]
 for box,t,c in res:
  if c<.12 or sum(ch.isalpha() for ch in t)<2:continue
  u=re.sub(r'[^A-Z]','',t.upper());xs=[float(p[0]) for p in box];ys=[float(p[1]) for p in box]
  h={'text':t,'confidence':float(c),'norm':u,'box':[min(xs),min(ys),max(xs),max(ys)]};hits.append(h)
  if len(u)>=2 and any(k in u or u in k for k in keys):bad.append((f.name,t,float(c),h['box']))
 rep[f.name]=hits
 print('\n###',f.name)
 for h in hits[:80]:print(repr(h['text']),round(h['confidence'],3),[round(x,1) for x in h['box']])
 print('TARGET_BAD',[x for x in bad if x[0]==f.name])
(D.parent/'button_global_probe_fix6_ocr.json').write_text(json.dumps({'bad':bad,'ocr':rep},ensure_ascii=False,indent=2),encoding='utf-8')
print('\nTOTAL_TARGET_BAD',len(bad))
