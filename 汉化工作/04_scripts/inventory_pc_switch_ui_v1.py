from pathlib import Path
import csv,struct,json,re,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
PC=Path(r'D:\switch游戏\个人汉化\clannad\pc汉化版\CLANNAD\【key】clannad fv')
BAK=PC/'clfvbak'
# changed pc g00 same-path
changed=[]
for p in PC.rglob('*.g00'):
    if 'clfvbak' in p.parts: continue
    rel=p.relative_to(PC)
    q=BAK/rel
    if q.exists() and hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(q.read_bytes()).digest():
        b=p.read_bytes(); fmt=b[0]; w=struct.unpack_from('<H',b,1)[0]; h=struct.unpack_from('<H',b,3)[0]
        changed.append((p.name.upper(),str(rel),fmt,w,h,p.stat().st_size))
# switch CZ headers: magic + headerlength at 4, width/height likely fields locate via known Luck header struct; try parse from code-derived offsets later. Here ask Go tool? inspect first 32 bytes.
for d in [R/'03_text/ui_work/SYSCG.PAK_unpacked',R/'03_text/ui_work/SYSCG2.PAK_unpacked',R/'03_text/ui_work/PARTS.PAK_unpacked',R/'03_text/switch_work/paks/MANUAL.PAK_unpacked']:
    if not d.exists():continue
    print('DIR',d.name)
    for f in sorted(d.iterdir())[:8]:
        if not f.is_file():continue
        b=f.read_bytes()[:32]
        print(f.name,len(f.read_bytes()),b.hex())
print('PC_CHANGED',len(changed))
from collections import Counter
print('PC_FORMATS',Counter(x[2] for x in changed))
print('PC_DIMS_TOP',Counter((x[3],x[4]) for x in changed).most_common(30))
out=R/'03_text/pc_ui/changed_g00_inventory.tsv'; out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter='\t');w.writerow(['name','rel','fmt','width','height','size']);w.writerows(changed)
print('SAMPLE_CHANGED')
for x in changed[:80]:print(x)
