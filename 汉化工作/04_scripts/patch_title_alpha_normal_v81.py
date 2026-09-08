from pathlib import Path
from PIL import Image
import csv,subprocess,json,shutil,numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); CZ=R/'tools/LuckSystem/tools/cztool/cztool.exe'
RAW=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked/TITLE'; SCAN=R/'05_build/ui_fullscan_english.tsv'; O=R/'05_build/title_alpha_fix2';O.mkdir(parents=True,exist_ok=True)
cur=O/'TITLE_fix1_current.png'; subprocess.run([str(CZ),'export',str(RAW),str(cur)],check=True)
im=Image.open(cur).convert('RGBA'); a=np.array(im); alpha=a[:,:,3].copy()
rows=list(csv.DictReader(SCAN.open(encoding='utf-8-sig'),delimiter='\t'))
want={'NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL'}
rr=[r for r in rows if r.get('asset')=='TITLE' and r.get('text','').strip() in want]
assert len(rr)==9,[(r.get('text'),r.get('asset')) for r in rr]
SHIFT=817; report=[]
# First clear every target normal-state slot, then copy the already-Chinese alpha mask from selected-state slot.
for r in rr:
 t=r['text'].strip();x1,y1,x2,y2=[int(round(float(r[k]))) for k in ('x1','y1','x2','y2')]
 pad=max(8,int((y2-y1)*.16)); sx1=max(0,x1-pad);sy1=max(0,y1-pad);sx2=min(im.width,x2+pad);sy2=min(im.height,y2+pad)
 tx1=sx1-SHIFT;tx2=sx2-SHIFT;ty1=sy1;ty2=sy2
 assert 0<=tx1<tx2<=im.width
 alpha[ty1:ty2,tx1:tx2]=0
 report.append({'text':t,'src':[sx1,sy1,sx2,sy2],'dst':[tx1,ty1,tx2,ty2]})
for ent in report:
 sx1,sy1,sx2,sy2=ent['src'];tx1,ty1,tx2,ty2=ent['dst']
 src=a[sy1:sy2,sx1:sx2,3]
 # Copy selected Chinese alpha exactly. Source region contains the fixed Chinese glyph mask.
 alpha[ty1:ty2,tx1:tx2]=src
# Preserve RGB exactly; replace only alpha.
a[:,:,3]=alpha
out=O/'TITLE_fix2_alpha.png';Image.fromarray(a,'RGBA').save(out)
tmp=O/'TITLE_fix2.cz'; subprocess.run([str(CZ),'import',str(RAW),str(out),str(tmp)],check=True)
probe=O/'TITLE_fix2_roundtrip.png';subprocess.run([str(CZ),'export',str(tmp),str(probe)],check=True)
p1=np.array(Image.open(out).convert('RGBA'));p2=np.array(Image.open(probe).convert('RGBA'))
print('ROUNDTRIP_EQUAL',bool(np.array_equal(p1,p2)),'DIFFPIX',int(np.any(p1!=p2,axis=2).sum()),'MAXDIFF',int(np.abs(p1.astype(int)-p2.astype(int)).max()))
# Sanity: RGB must be bit-identical to pre-patch, and alpha changed only intended target rectangles.
print('RGB_UNCHANGED',bool(np.array_equal(p1[:,:,:3],a[:,:,:3])))
print('ALPHA_CHANGED_PIX',int((p1[:,:,3]!=np.array(im)[:,:,3]).sum()))
(R/'05_build/title_alpha_fix2_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Commit only after exact cz3 roundtrip.
assert np.array_equal(p1,p2)
shutil.copy2(tmp,RAW)
print('COMMITTED',RAW)
for e in report:print(e)
