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
# find exact starts of RTTI strings, then pointer chains
for needle in [b'N4task10cTitleMenu10cScrSelectE',b'N4task10cTitleMenu12cLabelSelectE',b'N4task10cTitleMenu11cTitleMovieE',b'N4task10cTitleMenu12cStartEffectE']:
 o=r.find(needle);a=0x1A3000+o;print('\nSTRING',needle.decode(),hex(a))
 for target in range(a-16,a+8):
  q=struct.pack('<Q',target);hs=[];st=0
  while True:
   z=img.find(q,st)
   if z<0:break
   hs.append(z);st=z+1
  if hs:
   print('PTRTO',hex(target),[hex(x) for x in hs[:30]])
   for h in hs[:8]:
    q2=struct.pack('<Q',h);vs=[];s2=0
    while True:
     z2=img.find(q2,s2)
     if z2<0:break
     vs.append(z2);s2=z2+1
    if vs:print('  PTR2',hex(h),[hex(x) for x in vs[:30]])
