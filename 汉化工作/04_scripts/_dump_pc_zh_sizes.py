from pathlib import Path
from PIL import Image
D=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作\05_build\pc_ui_zh_png")
for p in sorted(D.glob('*.png')):
 with Image.open(p) as im:print(f'{p.stem}\t{im.width}x{im.height}')
