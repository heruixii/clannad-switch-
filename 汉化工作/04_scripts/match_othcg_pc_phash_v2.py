from pathlib import Path
from PIL import Image
import numpy as np,cv2,csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SW=R/'05_build/othcg_jp_reps_png'; PC=R/'05_build/pc_ui_orig_png'
def feat(p):
 im=np.array(Image.open(p).convert('L')); im=cv2.resize(im,(64,64),interpolation=cv2.INTER_AREA); d=cv2.dct(np.float32(im)); x=d[:16,:16]; med=np.median(x[1:]); return (x>med).flatten()
pc={p.stem:feat(p) for p in PC.glob('*.png')}
targets=['_68SNTEN00_EN','73SPAPA00_EN','73SPAPA10_EN']+[f'SFUSM00_{i:02d}_EN' for i in range(7)]+[f'SR_ALS_{i:02d}_EN' for i in range(1,6)]+[f'SR_ALS_NAME_{i}_EN' for i in range(1,4)]+[f'SR_NAME{a}_{b}_EN' for a in range(1,4) for b in range(1,4)]+['YAKYU_01_EN','YAKYU_02_EN','SPDATA00BTN_EN']
for t in targets:
 p=SW/(t+'.png');
 if not p.exists(): print('\n',t,'NOJP'); continue
 f=feat(p); sc=sorted(((int(np.count_nonzero(f!=v)),k) for k,v in pc.items()))[:8]
 print('\n',t,sc)
