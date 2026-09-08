from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');t=(D/'text.bin').read_bytes();r=(D/'rodata.bin').read_bytes();d=(D/'data.bin').read_bytes();size=max(0x212000+len(d),0x1A3000+len(r),len(t));img=bytearray(size);img[:len(t)]=t;img[0x1A3000:0x1A3000+len(r)]=r;img[0x212000:0x212000+len(d)]=d
rela=0x1a3058;relasz=0x30d98;dynsym=0x1d6008;syment=24

def symval(idx):
 o=dynsym+idx*syment
 if o+24>len(img):return 0
 name,info,other,shndx,val,sz=struct.unpack_from('<IBBHQQ',img,o)
 return val
stats={}
for i in range(relasz//24):
 off,info,add=struct.unpack_from('<QQq',img,rela+i*24);typ=info&0xffffffff;sym=info>>32;stats[typ]=stats.get(typ,0)+1
 if not(0<=off<=len(img)-8):continue
 if typ==1027:v=add
 elif typ==257:v=symval(sym)+add
 elif typ==1025:v=symval(sym)
 else:continue
 struct.pack_into('<Q',img,off,v & 0xffffffffffffffff)
print('stats',stats)
for nameaddr,label in [(0x1ec6f8,'cTitleMenu'),(0x1ec718,'cStartEffect'),(0x1ec748,'cTitleMovie'),(0x1ec778,'cScrSelect'),(0x1ec798,'cLabelSelect'),(0x1eb9e8,'cConfigWin')]:
 q=struct.pack('<Q',nameaddr);hits=[];st=0
 while True:
  o=img.find(q,st)
  if o<0:break
  hits.append(o);st=o+1
 print('\nNAMEPTR',label,[hex(x) for x in hits[:30]])
 for h in hits[:10]:
  q2=struct.pack('<Q',h);vh=[];st2=0
  while True:
   o2=img.find(q2,st2)
   if o2<0:break
   vh.append(o2);st2=o2+1
  if vh:print(' type',hex(h),'ptrs',[hex(x) for x in vh[:30]])
