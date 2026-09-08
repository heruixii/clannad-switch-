from pathlib import Path
import struct,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');ro=(D/'rodata.bin').read_bytes();RB=0x1A3000
for start in [0x1c1c80,0x1c1cc0,0x1c1cf0,0x1c1d20,0x1c2390,0x1c23c0]:
 print('\n###',hex(start))
 o=start-RB
 for i in range(0,0xc0,8):
  a=start+i;v=struct.unpack_from('<Q',ro,o+i)[0]
  tag='TEXT' if 0<v<0x1A3000 else ('RO' if RB<=v<RB+len(ro) else '')
  s=''
  if tag=='RO':
   oo=v-RB;e=ro.find(b'\0',oo,min(len(ro),oo+100));e=e if e>=0 else min(len(ro),oo+100)
   try:s=ro[oo:e].decode('utf-8')
   except:s=''
  print(hex(a),hex(v),tag,s[:80])
