from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'02_romfs/merged-v1.0.7'
terms=['Configuration','Message Speed','Text Speed','Auto Mode','Skip Mode','Voice Volume','BGM Volume','Sound Volume','Window','Opacity','Vibration','Button 1','Button 2','Touch','Basic','Language','Display','Font','Read Text','Unread Text','Quick Save','Quick Load']
for p in D.glob('*.PAK'):
 b=p.read_bytes(); hits=[]
 for t in terms:
  for enc in ['utf-16le','ascii','utf-8']:
   q=t.encode(enc); i=b.find(q)
   if i>=0:hits.append((i,enc,t))
 if hits:
  print('###',p.name,p.stat().st_size)
  for x in sorted(hits):print(*x)
