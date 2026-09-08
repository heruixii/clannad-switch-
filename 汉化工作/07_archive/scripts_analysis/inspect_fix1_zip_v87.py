from pathlib import Path
import zipfile
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\CLANNAD_CHS_LayeredFS_v1.0.7_fix1.zip')
with zipfile.ZipFile(p) as z:
 print('\n'.join(z.namelist()[:30]))
