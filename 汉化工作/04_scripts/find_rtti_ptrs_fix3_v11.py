from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
parts=[('text',0,D/'text.bin'),('ro',0x1A3000,D/'rodata.bin'),('data',0x212000,D/'data.bin')]
for a in [0x1ec6f8,0x1ec718,0x1ec748,0x1ec778,0x1ec798,0x1eb9e8]:
 q=struct.pack('<Q',a);print('\nADDR',hex(a))
 for name,base,p in parts:
  b=p.read_bytes();st=0;hs=[]
  while True:
   o=b.find(q,st)
   if o<0:break
   hs.append(base+o);st=o+1
  if hs:print(name,[hex(x) for x in hs[:50]])
