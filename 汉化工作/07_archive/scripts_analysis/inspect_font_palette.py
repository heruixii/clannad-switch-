from pathlib import Path
import struct,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_work\paks\FONT.PAK_unpacked\ゴシック24')
b=p.read_bytes();hl=struct.unpack_from('<I',b,4)[0];vals=[]
for i in range(256):
 B,G,R,A=b[hl+i*4:hl+i*4+4];vals.append((R,G,B,A))
print('identity_alpha',sum(1 for i,x in enumerate(vals) if x[3]==i),'of 256')
print('unique_alpha',len(set(x[3] for x in vals)))
print('first64',[(i,vals[i]) for i in range(64)])
print('last32',[(i,vals[i]) for i in range(224,256)])
