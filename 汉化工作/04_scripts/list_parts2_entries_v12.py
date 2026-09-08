from pathlib import Path
import struct
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\ui_work\PARTS2.PAK'); b=p.read_bytes(); hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];u=lambda o:struct.unpack_from('<I',b,o)[0];pos=32;marker=hl//bs
while u(pos)!=marker:pos+=4
q=u(pos-4);names=[]
for i in range(fc):
 z=b.find(b'\0',q,hl);names.append(b[q:z].decode('utf-8','replace'));q=z+1
print('hl',hl,'fc',fc,'bs',bs,'flags',hex(flags),'pos',pos)
for i,n in enumerate(names):
 bo,ln=struct.unpack_from('<II',b,pos+i*8);print(i,n,ln,bo*bs)
