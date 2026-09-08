from pathlib import Path
from PIL import Image
import json,numpy as np
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); O=R/'05_build/title_alpha_fix2'; rep=json.loads((R/'05_build/title_alpha_fix2_report.json').read_text(encoding='utf-8'))
fix1=np.array(Image.open(O/'TITLE_fix1_current.png').convert('RGBA'))[:,:,3]
fix2=np.array(Image.open(O/'TITLE_fix2_roundtrip.png').convert('RGBA'))[:,:,3]
orig=np.array(Image.open(R/'05_build/title_state_probe/TITLE.png').convert('RGBA'))[:,:,3]
for e in rep:
 sx1,sy1,sx2,sy2=e['src'];tx1,ty1,tx2,ty2=e['dst']
 s=fix1[sy1:sy2,sx1:sx2];so=orig[sy1:sy2,sx1:sx2];t=fix2[ty1:ty2,tx1:tx2];to=fix1[ty1:ty2,tx1:tx2]
 def stat(a):return {'shape':a.shape,'nz>8':int((a>8).sum()),'nz>64':int((a>64).sum()),'nz>200':int((a>200).sum()),'mean':round(float(a.mean()),2)}
 print(e['text'],'SRC',stat(s),'SRC_ORIG',stat(so),'SRC_CHANGED',int((s!=so).sum()),'TARGET',stat(t),'TARGET_OLD',stat(to),'TARGET_CHANGED',int((t!=to).sum()))
