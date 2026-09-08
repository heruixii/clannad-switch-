from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
parts=[('text',0,D/'text.bin'),('rodata',0x1A3000,D/'rodata.bin'),('data',0x212000,D/'data.bin')]
terms=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL','New Game','After Story','CG Mode','Music Mode','Config','Name','Dangopedia','Manual']
encs={'ascii':lambda s:s.encode('ascii'),'utf16le':lambda s:s.encode('utf-16le'),'utf32le':lambda s:s.encode('utf-32le'),'sjis':lambda s:s.encode('shift_jis')}
for name,base,p in parts:
 b=p.read_bytes();print('\n##',name)
 for t in terms:
  hs=[]
  for en,fn in encs.items():
   q=fn(t);st=0
   while 1:
    o=b.find(q,st)
    if o<0:break
    hs.append((en,base+o));st=o+1
  if hs:print(t,[(e,hex(a)) for e,a in hs])
