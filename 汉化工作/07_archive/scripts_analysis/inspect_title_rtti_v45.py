from pathlib import Path
import struct,binascii
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed'); ro=(D/'rodata.bin').read_bytes(); data=(D/'data.bin').read_bytes(); RB=0x1A3000; DB=0x212000
for a in [0x1ec680,0x1ec6d0,0x1ec6f0,0x1ec710,0x1ec740,0x1ec770,0x1ec790]:
 o=a-RB; print('\nRO',hex(a)); print(binascii.hexlify(ro[o:o+160]).decode()); print(ro[o:o+160].decode('utf-8','ignore').replace('\x00','·'))
# Search 64-bit little-endian pointers to RTTI names across rodata/data
for target in [0x1ec6f0,0x1ec710,0x1ec740,0x1ec770,0x1ec790]:
 q=struct.pack('<Q',target); hits=[]
 for name,b,base in [('ro',ro,RB),('data',data,DB)]:
  st=0
  while 1:
   x=b.find(q,st)
   if x<0:break
   hits.append((name,hex(base+x))); st=x+1
 print('PTR',hex(target),hits[:50])
# Search 32bit rel values that could resolve to target: field value = target - field_addr
for target in [0x1ec6f0,0x1ec710,0x1ec740,0x1ec770,0x1ec790]:
 hits=[]
 for name,b,base in [('ro',ro,RB),('data',data,DB)]:
  for off in range(0,len(b)-4,4):
   v=struct.unpack_from('<i',b,off)[0]
   if base+off+v==target:hits.append((name,hex(base+off),hex(v & 0xffffffff)))
 print('REL32',hex(target),hits[:40])
