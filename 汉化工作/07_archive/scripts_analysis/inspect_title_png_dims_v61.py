from pathlib import Path
from PIL import Image,ImageStat
root=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\title_state_probe')
for p in sorted(root.glob('TITLE*.png')):
 im=Image.open(p).convert('RGBA'); a=im.getchannel('A'); bbox=a.getbbox(); ext=a.getextrema(); print(p.name,im.size,'alpha',ext,'bbox',bbox,'bytes',p.stat().st_size)
