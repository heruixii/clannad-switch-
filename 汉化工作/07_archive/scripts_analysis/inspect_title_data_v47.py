from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');data=(D/'data.bin').read_bytes();DB=0x212000
for start in [0x23d0d0,0x23d100,0x23d110,0x23d128,0x23d130,0x23d148,0x23d150,0x23d160,0x23d168,0x23d170,0x23d178,0x23d180,0x23d380,0x23d390,0x23d3a8,0x23d3b0,0x23d3b8]:
 print('\n###',hex(start));o=start-DB
 for i in range(0,0x60,8):
  if o+i+8>len(data):break
  v=struct.unpack_from('<Q',data,o+i)[0]
  tag='TEXT' if 0<v<0x1A3000 else ('RO' if 0x1A3000<=v<0x212000 else ('DATA' if DB<=v<DB+len(data) else ''))
  print(hex(start+i),hex(v),tag)
