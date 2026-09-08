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
for base,label in [(0x1ec6f0,'title'),(0x1eb9e0,'config')]:
 print('\n',label)
 for target in range(base,base+0x30):
  q=struct.pack('<Q',target);st=0;hs=[]
  while 1:
   o=img.find(q,st)
   if o<0:break
   hs.append(o);st=o+1
  if hs:print(hex(target),[hex(x) for x in hs[:20]])
