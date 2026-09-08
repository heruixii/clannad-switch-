from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
parts=[('text',0x0,D/'text.bin'),('rodata',0x1A3000,D/'rodata.bin'),('data',0x212000,D/'data.bin')]
terms=['NEW GAME','New Game','Game Start','LOAD','Load','AFTER STORY','After Story','CG MODE','CG Mode','MUSIC MODE','Music Mode','CONFIG','Config','NAME','Name','DANGOPEDIA','Dangopedia','MANUAL','Manual']
for name,base,p in parts:
 b=p.read_bytes();print('\n##',name)
 for t in terms:
  q=t.encode();st=0;hits=[]
  while True:
   o=b.find(q,st)
   if o<0:break
   lo=max(0,o-32);hi=min(len(b),o+len(q)+48);ctx=b[lo:hi]
   hits.append((hex(base+o),ctx.hex(),ctx.decode('utf-8','replace').replace('\x00','·')));st=o+1
  if hits:
   print('\nTERM',t,'count',len(hits))
   for h in hits[:30]:print(h)
