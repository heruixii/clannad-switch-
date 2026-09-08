from fontTools.ttLib import TTCollection
from pathlib import Path
out=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\font_sources_internal')
for inp,name,idx in [(r'C:\Windows\Fonts\msyhbd.ttc','msyhbd-face0.ttf',0),(r'C:\Windows\Fonts\msyh.ttc','msyh-face0.ttf',0)]:
 c=TTCollection(inp); c.fonts[idx].save(out/name); print(name,(out/name).stat().st_size)
