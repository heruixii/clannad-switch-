from pathlib import Path
from PIL import Image
import csv, math
R=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
pc=R/'05_build/pc_ui_orig_png'; sw=R/'05_build/othcg_reps_png'
print('pc',len(list(pc.glob('*.png'))),'sw',len(list(sw.glob('*.png'))))
from collections import Counter
for label,d in [('pc',pc),('sw',sw)]:
 c=Counter()
 for p in d.glob('*.png'):
  with Image.open(p) as im:c[(im.width,im.height)]+=1
 print('\n',label,'top sizes')
 for k,n in c.most_common(30):print(n,k)
