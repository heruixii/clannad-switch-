from pathlib import Path
import struct
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\font_probe\gothic24.cz2');b=p.read_bytes();hl,w,h=struct.unpack_from('<IHH',b,4);pos=hl+1024;fc=struct.unpack_from('<I',b,pos)[0];pos+=4;s=[]
for _ in range(fc): cs,rs=struct.unpack_from('<II',b,pos);pos+=8;s.append((cs,rs))
for bi,(cs,rs) in enumerate(s):
 codes=list(struct.unpack_from('<'+'H'*(cs//2),b,pos));pos+=cs
 hi=[i for i,x in enumerate(codes) if x>=65530]
 print('BLOCK',bi,'codes',len(codes),'raw',rs,'hi_count',len(hi),'first_hi',hi[:20])
 for i in hi[:8]:print(i,codes[max(0,i-8):i+12])
