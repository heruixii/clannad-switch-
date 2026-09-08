from pathlib import Path
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\rodata.bin').read_bytes();B=0x1A3000
for q in [b'TITLE',b'Title',b'title',b'SYSCG/',b'TITLE_P']:
 print('\nTERM',q)
 st=0;n=0
 while 1:
  o=b.find(q,st)
  if o<0:break
  lo=max(0,o-80);hi=min(len(b),o+160);ctx=b[lo:hi].decode('utf-8','replace').replace('\x00','·')
  print(hex(B+o),ctx);n+=1;st=o+1
 print('count',n)
