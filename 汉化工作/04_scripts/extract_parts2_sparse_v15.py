from pathlib import Path
import struct,shutil,subprocess
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); P=R/'03_text/ui_work/PARTS2.PAK'; O=R/'05_build/parts2_sparse'; O.mkdir(parents=True,exist_ok=True)
b=P.read_bytes();hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);pos=40
names={8:'CONFIG_BG',9:'CONFIG_BG_EN',12:'CONFIG_TAB',13:'CONFIG_TAB_EN',116:'EXTRA_64116'}
for i in range(fc):
 off,ln=struct.unpack_from('<II',b,pos+i*8)
 if not(off or ln):continue
 n=names.get(i,f'ID_{idstart+i}');q=O/n;q.write_bytes(b[off*bs:off*bs+ln]);print(i,idstart+i,n,ln,q)
