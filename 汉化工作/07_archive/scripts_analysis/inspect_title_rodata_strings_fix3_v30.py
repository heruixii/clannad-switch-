from pathlib import Path
import re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');rb=(D/'rodata.bin').read_bytes();B=0x1A3000
# list printable UTF-8/ASCII strings around known uppercase title words
for center in [0x1deb57,0x1dd22f,0x1de3f6,0x1dd99a,0x1de46f]:
 o=center-B;lo=max(0,o-0x300);hi=min(len(rb),o+0x500);print('\n### CENTER',hex(center))
 pos=lo
 while pos<hi:
  z=rb.find(b'\0',pos,hi)
  if z<0:break
  raw=rb[pos:z]
  if len(raw)>=2:
   try:s=raw.decode('utf-8')
   except:s=''
   if s and sum(c.isprintable() for c in s)>=len(s)*.9:print(hex(B+pos),repr(s))
  pos=z+1
# all exact title-like uppercase/string variants in rodata with addresses
terms=[b'NEW GAME',b'LOAD',b'AFTER STORY',b'CG MODE',b'MUSIC MODE',b'CONFIG',b'NAME',b'DANGOPEDIA',b'MANUAL',b'Game Start',b'Music Mode',b'Dangopedia',b'Manual']
print('\n### EXACT')
for q in terms:
 st=0
 while True:
  o=rb.find(q+b'\0',st)
  if o<0:break
  print(q.decode(),hex(B+o));st=o+1
