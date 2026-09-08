from pathlib import Path
import json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');b=(D/'rodata.bin').read_bytes();mem=0x1A3000
terms=['NEW GAME','New Game','LOAD','Load','AFTER STORY','After Story','CG MODE','CG Mode','MUSIC MODE','Music Mode','CONFIG','Config','NAME','Name','DANGOPEDIA','Dangopedia','MANUAL','Manual','Configuration','Basic','Button1','Button2','Touch','Text1','Text2','Sound','Voice','Screen','Auto-Sleep','Green Level','Blue Level','Quick Load','Quick Save']
rows=[]
for t in terms:
 q=t.encode();st=0
 while True:
  o=b.find(q,st)
  if o<0:break
  lo=max(0,o-72);hi=min(len(b),o+len(q)+120);ctx=b[lo:hi].decode('utf-8','ignore');ctx=''.join(c if ord(c)>=32 else '·' for c in ctx)
  rows.append({'term':t,'ro_offset':o,'nso_memory_offset':mem+o,'context':ctx});st=o+len(q)
print(json.dumps(rows,ensure_ascii=False,indent=2));(D/'ui_hits_v37.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('HITS',len(rows))
