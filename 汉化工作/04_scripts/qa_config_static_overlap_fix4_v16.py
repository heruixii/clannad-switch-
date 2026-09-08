from pathlib import Path
from PIL import Image
import numpy as np,cv2,easyocr,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');C=R/'05_build/config_fix4';P2=R/'05_build/parts2_sparse'
def erase(en,base):
 A=np.array(en.convert('RGBA'));B=np.array(base.convert('RGBA'));d=np.max(np.abs(A.astype(np.int16)-B.astype(np.int16)),axis=2);m=(d>4).astype(np.uint8)*255;m=cv2.dilate(m,np.ones((5,5),np.uint8),iterations=1);O=A.copy()
 for c in range(4):O[:,:,c]=cv2.inpaint(A[:,:,c],m,3,cv2.INPAINT_TELEA)
 return O
cleanbg=erase(Image.open(P2/'CONFIG_BG_EN.png'),Image.open(P2/'CONFIG_BG.png'));cleantab=erase(Image.open(P2/'CONFIG_TAB_EN.png'),Image.open(P2/'CONFIG_TAB.png'))
bg=np.array(Image.open(C/'PARTS2_CONFIG_BG_CHS.verify.png').convert('RGBA'));tab=np.array(Image.open(C/'PARTS2_CONFIG_TAB_CHS.verify.png').convert('RGBA'))
db=np.max(np.abs(bg.astype(np.int16)-cleanbg.astype(np.int16)),axis=2);dt=np.max(np.abs(tab.astype(np.int16)-cleantab.astype(np.int16)),axis=2)
# isolate tab glyph change bands; BG title excluded by x>=333
mb=(db>3);mt=(dt>3);mb[:,:333]=False;mb[:,1890:]=False;mb[100:,:]=False;mt[:,:333]=False;mt[:,1890:]=False
# shift TAB source mask down 14 to BG coordinates
mts=np.zeros_like(mb);mts[14:94,:]=mt[:80,:]
A=mb[10:100,333:1890];B=mts[10:100,333:1890];inter=int((A&B).sum());union=int((A|B).sum());iou=inter/union if union else 1;xor=int((A^B).sum())
print('TAB_LAYER_IOU_AFTER_14PX',iou,'XOR',xor,'BGPIX',int(A.sum()),'TABPIX',int(B.sum()))
# OCR English leftovers across authoritative P2 and neutral P1
rd=easyocr.Reader(['en'],gpu=False,verbose=False,download_enabled=False);old=['CONFIGURATION','BASIC','BUTTON','TOUCH','TEXT','SOUND','VOICE','SCREEN','ENGLISH','QUICK LOAD','CLOSE','DEFAULTS'];ocr={};bad=[]
files=['PARTS2_CONFIG_BG_CHS.verify.png','PARTS2_CONFIG_TAB_CHS.verify.png','PARTS1_CONFIG_BG_NEUTRAL.verify.png','PARTS1_CONFIG_BG_EN_NEUTRAL.verify.png','PARTS1_CONFIG_TAB_NEUTRAL.verify.png','PARTS1_CONFIG_TAB_EN_NEUTRAL.verify.png']
for fn in files:
 im=np.array(Image.open(C/fn).convert('RGB'));res=rd.readtext(im,detail=1,paragraph=False,canvas_size=3200,mag_ratio=1.5,text_threshold=.22,low_text=.06,link_threshold=.12);hits=[]
 for box,t,c in res:
  if c<.18 or sum(ch.isalpha() for ch in t)<2:continue
  u=re.sub(r'[^A-Z ]',' ',t.upper());u=' '.join(u.split());hits.append((t,float(c)))
  if any(k in u or u in k for k in old if len(u)>=3):bad.append((fn,t,float(c)))
 ocr[fn]=hits[:80];print(fn,'OLD_BAD',[x for x in bad if x[0]==fn])
rep={'tab_layer_iou_after_14px':iou,'tab_layer_xor':xor,'bg_mask_pixels':int(A.sum()),'tab_mask_pixels':int(B.sum()),'english_bad':bad,'ocr':ocr}
(R/'05_build/config_fix4_static_qa.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL_OLD_ENGLISH_BAD',len(bad))
if bad or iou<0.85:raise SystemExit(2)
