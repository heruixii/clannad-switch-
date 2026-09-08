from pathlib import Path
import re,binascii,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');b=p.read_bytes()
terms=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','Dangopedia','MANUAL','Configuration','Basic','Button1','Button2','Touch','Text1','Text2','Sound','Voice','Screen','Language','Quick Load','Quick Save','Backlog','Auto-Sleep','Green Level','Blue Level']
rep=[]
for t in terms:
 q=t.encode('utf-8');start=0
 while True:
  o=b.find(q,start)
  if o<0:break
  # extract nearby ASCII runs length>=3
  lo=max(0,o-256);hi=min(len(b),o+len(q)+256);chunk=b[lo:hi]
  runs=[]
  for m in re.finditer(rb'[\x20-\x7e]{3,}',chunk):
   runs.append({'rel':m.start()-(o-lo),'text':m.group().decode('ascii','replace')})
  rep.append({'term':t,'offset':o,'runs':runs[:80],'hex':binascii.hexlify(b[max(0,o-64):min(len(b),o+len(q)+64)]).decode()})
  start=o+len(q)
print(json.dumps(rep,ensure_ascii=False,indent=2));(p.parent/'main_ui_cluster_v26.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print('HITS',len(rep))
