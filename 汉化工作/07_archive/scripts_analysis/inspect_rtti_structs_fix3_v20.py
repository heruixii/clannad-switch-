from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');t=(D/'text.bin').read_bytes();r=(D/'rodata.bin').read_bytes();d=(D/'data.bin').read_bytes();size=max(0x212000+len(d),0x1A3000+len(r),len(t));img=bytearray(size);img[:len(t)]=t;img[0x1A3000:0x1A3000+len(r)]=r;img[0x212000:0x212000+len(d)]=d
rela=0x1a3058;relasz=0x30d98;dynsym=0x1d6008
def sym(idx):return struct.unpack_from('<IBBHQQ',img,dynsym+idx*24)
for i in range(relasz//24):
 off,info,add=struct.unpack_from('<QQq',img,rela+i*24);typ=info&0xffffffff;si=info>>32
 if typ==1027:v=add
 elif typ in (257,1025):v=sym(si)[4]+(add if typ==257 else 0)
 else:continue
 if 0<=off<=len(img)-8:struct.pack_into('<Q',img,off,v&0xffffffffffffffff)
for a in [0x1c1cc0,0x23d0e0,0x1c1cf0,0x23d110,0x1bbfd8,0x23aef8]:
 print('\nAT',hex(a))
 for o in range(a,a+0x80,8):
  if o+8<=len(img):print(hex(o),hex(struct.unpack_from('<Q',img,o)[0]))
