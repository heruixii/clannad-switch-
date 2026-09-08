from pathlib import Path
import struct,binascii
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');t=(D/'text.bin').read_bytes();r=(D/'rodata.bin').read_bytes();d=(D/'data.bin').read_bytes();img=bytearray(0x212000+len(d));img[:len(t)]=t;img[0x1A3000:0x1A3000+len(r)]=r;img[0x212000:0x212000+len(d)]=d
for a in [0x246ce0,0x246ce8,0x246cf0,0x246cd0]:
 print('\n',hex(a),binascii.hexlify(img[a:a+128]).decode())
 for i in range(5):
  print(i,struct.unpack_from('<QQ',img,a+i*16))
