from pathlib import Path
from fontTools.ttLib import TTFont,TTCollection
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
chars=(R/'05_build/font_patch_plan/missing_chars_v2.txt').read_text(encoding='utf-8').strip()
paths=[r'C:\Windows\Fonts\NotoSansSC-VF.ttf',r'C:\Windows\Fonts\NotoSerifSC-VF.ttf',r'C:\Windows\Fonts\MiSans-Regular.otf',r'C:\Windows\Fonts\msyh.ttc',r'C:\Windows\Fonts\msyhbd.ttc',r'C:\Windows\Fonts\simhei.ttf',r'C:\Windows\Fonts\simsun.ttc',r'C:\Windows\Fonts\STZHONGS.TTF',r'C:\Windows\Fonts\YuGothB.ttc',r'C:\Windows\Fonts\msgothic.ttc']
for p in paths:
    if not Path(p).exists(): continue
    fs=TTCollection(p).fonts if p.lower().endswith('.ttc') else [TTFont(p)]
    for i,f in enumerate(fs):
        cmap=f.getBestCmap() or {}; miss=[c for c in chars if ord(c) not in cmap]
        nm=''
        for n in f['name'].names:
            if n.nameID==1:
                try:nm=n.toUnicode();break
                except:pass
        print(Path(p).name,i,nm,'coverage',len(chars)-len(miss),'/',len(chars),'missing',len(miss),'preview',''.join(miss[:30]))
