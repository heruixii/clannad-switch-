from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs')
terms=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL','New Game','After Story','Music Mode','Dangopedia']
for f in D.iterdir():
 if not f.is_file():continue
 b=f.read_bytes();hits=[]
 for t in terms:
  for enc in ['ascii','utf-16le','utf-16be']:
   q=t.encode(enc);st=0
   while True:
    o=b.find(q,st)
    if o<0:break
    hits.append((t,enc,o));st=o+1
 if hits:
  print('\n',f.name,f.stat().st_size)
  for h in hits:print(h)
