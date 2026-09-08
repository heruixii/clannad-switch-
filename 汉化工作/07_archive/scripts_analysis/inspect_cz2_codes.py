from pathlib import Path
import struct
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\font_probe\gothic24.cz2')
b=p.read_bytes(); sig=b[:4];hl,w,h=struct.unpack_from('<IHH',b,4);bits=b[12]
pos=hl
# palette 256*4 for 8bit
pos+=256*4
fc=struct.unpack_from('<I',b,pos)[0];pos+=4
sizes=[]
for i in range(fc):
 cs,rs=struct.unpack_from('<II',b,pos);pos+=8;sizes.append((cs,rs))
print(sig,hl,w,h,bits,'fc',fc,'sizes first',sizes[:10],'pos',pos,'len',len(b),'sumcs',sum(x[0] for x in sizes),'pixels',w*h)
for bi,(cs,rs) in enumerate(sizes[:3]):
 codes=struct.unpack_from('<'+'H'*(min(cs,100)//2),b,pos)
 print('block',bi,'cs',cs,'rs',rs,'codes',codes[:50])
 pos+=cs
