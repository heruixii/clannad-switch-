from pathlib import Path
from PIL import Image
import numpy as np,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SRC=R/'05_build/ui_png_en'; TAR=R/'05_build/ui_png_zh_v3'; CZ=R/'05_build/ui_cz_v3/MANUAL'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
assets=['EN_MANUAL01_LINKTO_1_02','EN_MANUAL01_LINKTO_6_17','EN_MANUAL01_LINKTO_7_25','EN_MANUAL01_LINKTO_8_26']
for a in assets:
 o=np.array(Image.open(SRC/(a+'.png')).convert('RGBA'),dtype=np.int16); t=np.array(Image.open(TAR/(a+'.png')).convert('RGBA'),dtype=np.int16)
 pal=np.unique(o.reshape(-1,4),axis=0)
 uniq,inv=np.unique(t.reshape(-1,4),axis=0,return_inverse=True)
 # alpha weighted strongly to keep transparency structure
 d=uniq[:,None,:].astype(np.int32)-pal[None,:,:].astype(np.int32); d[:,:,3]*=2
 idx=np.argmin(np.sum(d*d,axis=2),axis=1); q=pal[idx][inv].reshape(t.shape).astype(np.uint8)
 Image.fromarray(q,'RGBA').save(TAR/(a+'.png'))
 subprocess.run([str(EXE),'import',str(R/'03_text/switch_work/paks/MANUAL.PAK_unpacked'/a),str(TAR/(a+'.png')),str(CZ/a)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print(a,'orig_palette',len(pal),'target_unique',len(uniq),'quant_unique',len(np.unique(q.reshape(-1,4),axis=0)))
