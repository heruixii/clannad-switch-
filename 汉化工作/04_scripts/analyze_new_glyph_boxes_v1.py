from pathlib import Path
from PIL import Image
import csv,statistics,collections
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); im=Image.open(R/'05_build/font_patched_probe.png').convert('RGBA'); A=im.getchannel('A'); bs=25
rows=[]
with (R/'05_build/font_patch_plan/slot_map_v2.tsv').open(encoding='utf-8-sig') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  i=int(r['index']); ch=r['new_char']; x=i%100;y=i//100; b=A.crop((x*bs,y*bs,(x+1)*bs,(y+1)*bs)).getbbox(); rows.append((i,ch,b))
print('new',len(rows),'blank',sum(1 for _,_,b in rows if not b))
for label,vals in [('top',[b[1] for _,_,b in rows if b]),('bottom',[b[3] for _,_,b in rows if b]),('height',[b[3]-b[1] for _,_,b in rows if b])]:
 print(label,'min',min(vals),'median',statistics.median(vals),'mode',collections.Counter(vals).most_common(10),'max',max(vals))
print('extremes top>=3 or bottom<=20')
for i,ch,b in rows:
 if b and (b[1]>=3 or b[3]<=20): print(i,ch,b)
