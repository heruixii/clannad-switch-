from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');t=(D/'text.bin').read_bytes();r=(D/'rodata.bin').read_bytes();d=(D/'data.bin').read_bytes();size=max(0x212000+len(d),0x1A3000+len(r),len(t));img=bytearray(size);img[:len(t)]=t;img[0x1A3000:0x1A3000+len(r)]=r;img[0x212000:0x212000+len(d)]=d
rela=0x1a3058;relasz=0x30d98;count=relasz//24;applied=0;types={}
for i in range(count):
 off,info,add=struct.unpack_from('<QQq',img,rela+i*24);typ=info&0xffffffff;types[typ]=types.get(typ,0)+1
 if typ==1027 and 0<=off<=len(img)-8:
  struct.pack_into('<Q',img,off,add & 0xffffffffffffffff);applied+=1
print('rela',count,'types',types,'applied',applied)
for nameaddr,label in [(0x1ec6f8,'cTitleMenu'),(0x1ec718,'cStartEffect'),(0x1ec748,'cTitleMovie'),(0x1ec778,'cScrSelect'),(0x1ec798,'cLabelSelect'),(0x1eb9e8,'cConfigWin')]:
 q=struct.pack('<Q',nameaddr);hits=[];st=0
 while True:
  o=img.find(q,st)
  if o<0:break
  hits.append(o);st=o+1
 print('\nNAMEPTR',label,hex(nameaddr),[hex(x) for x in hits[:30]])
 # for each typeinfo candidate, find pointers to it (vtables)
 for h in hits[:10]:
  q2=struct.pack('<Q',h);vh=[];st2=0
  while True:
   o2=img.find(q2,st2)
   if o2<0:break
   vh.append(o2);st2=o2+1
  if vh: print(' typeinfo?',hex(h),'ptrs',[hex(x) for x in vh[:30]])
