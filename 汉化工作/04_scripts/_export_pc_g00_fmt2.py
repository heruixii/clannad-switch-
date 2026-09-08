from pathlib import Path
import sys
sys.path.insert(0,str(Path(r"D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts")))
from decode_g00_v1 import decode
R=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
PC=Path(r"D:\switch游戏\个人汉化\clannad\pc汉化版\CLANNAD\【key】clannad fv")
for src,out in [(PC/'clfvbak/G00',R/'05_build/pc_ui_orig_png'),(PC/'G00',R/'05_build/pc_ui_zh_png')]:
    out.mkdir(parents=True,exist_ok=True); ok=bad=skip=0
    names={p.name for p in (PC/'clfvbak/G00').glob('*.g00')}
    for name in sorted(names):
        p=src/name
        if not p.exists(): skip+=1; continue
        b=p.read_bytes()
        if not b or b[0]!=2: skip+=1; continue
        try:
            im=decode(p); im.save(out/(p.stem+'.png')); ok+=1
        except Exception as e:
            print('FAIL',p.name,repr(e)); bad+=1
    print(src,'ok',ok,'bad',bad,'skip',skip)
