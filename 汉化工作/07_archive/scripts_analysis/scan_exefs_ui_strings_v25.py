from pathlib import Path
import re,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs')
terms=['NEW GAME','LOAD','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','NAME','DANGOPEDIA','MANUAL','Configuration','Basic','Button1','Button2','Touch','Text1','Text2','Sound','Voice','Screen','Language','Window','Skip','Auto','Backlog','Save','Load','Title']
rep=[]
for p in sorted(x for x in D.iterdir() if x.is_file() and x.name!='EXEFS_HASHES.json'):
 b=p.read_bytes()
 for term in terms:
  for enc in ['ascii','utf-8','utf-16le','utf-16be']:
   try:q=term.encode(enc)
   except:continue
   start=0
   while True:
    o=b.find(q,start)
    if o<0:break
    lo=max(0,o-96);hi=min(len(b),o+len(q)+160);ctx=b[lo:hi]
    # printable approximation for context in matching encoding
    try:s=ctx.decode(enc,errors='replace')
    except:s=''
    rep.append({'file':p.name,'term':term,'encoding':enc,'offset':o,'context':s.replace('\x00','')[:260]})
    start=o+max(1,len(q))
print(json.dumps(rep,ensure_ascii=False,indent=2));(D/'ui_string_hits_v25.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL_HITS',len(rep))
