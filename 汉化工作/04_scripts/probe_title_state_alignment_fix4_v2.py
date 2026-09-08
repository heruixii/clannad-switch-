from pathlib import Path
from PIL import Image
import numpy as np,csv,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');P=R/'05_build/title_fix3/TITLE_fix3.verify.png';im=np.array(Image.open(P).convert('RGBA'));rows=list(csv.DictReader((R/'05_build/ui_fullscan_english.tsv').open(encoding='utf-8-sig'),delimiter='\t'));keys={'NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL'}
rep=[]
for r in rows:
 if r.get('asset')!='TITLE' or r.get('text','').strip() not in keys:continue
 k=r['text'].strip();x1,y1,x2,y2=[int(round(float(r[z]))) for z in ('x1','y1','x2','y2')];pad=max(3,int((y2-y1)*.12));rx1=max(0,x1-pad);rx2=min(im.shape[1],x2+pad);yy1=max(0,y1-pad);yy2=min(im.shape[0],y2+pad);lx1=rx1-817;lx2=rx2-817
 # alpha masks within same size boxes
 Rm=im[yy1:yy2,rx1:rx2,3]>64;Lm=im[yy1:yy2,lx1:lx2,3]>64
 inter=int((Rm&Lm).sum());union=int((Rm|Lm).sum());iou=inter/union if union else 1
 # bboxes local
 def bb(m):
  ys,xs=np.where(m)
  return None if len(xs)==0 else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1),int(m.sum())]
 rep.append({'text':k,'right_box':[rx1,yy1,rx2,yy2],'left_box':[lx1,yy1,lx2,yy2],'right_alpha':bb(Rm),'left_alpha':bb(Lm),'iou_shifted':iou,'xor':int((Rm^Lm).sum())})
print(json.dumps(rep,ensure_ascii=False,indent=2))
(R/'05_build/title_state_alignment_fix4_probe.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
