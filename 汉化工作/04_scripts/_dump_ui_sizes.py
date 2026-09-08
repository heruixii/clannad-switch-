from pathlib import Path
from PIL import Image
R=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
for label,d in [('PC',R/'05_build/pc_ui_orig_png'),('SW',R/'05_build/othcg_reps_png')]:
 print('\n###',label)
 for p in sorted(d.glob('*.png')):
  with Image.open(p) as im: print(f'{p.stem}\t{im.width}x{im.height}')
