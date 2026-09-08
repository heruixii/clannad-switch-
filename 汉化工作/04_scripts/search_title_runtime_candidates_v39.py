from pathlib import Path
import re,json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');b=(D/'rodata.bin').read_bytes();mem=0x1A3000
terms=['Game Start','Start Game','Load Game','Load','After','Story','CG','Music Mode','MUSIC MODE','Config','Settings','Name Edit','Name','Dangopedia','Manual','Continue','New Game','NEW GAME','AFTER','TITLE','Title']
rows=[]
for t in terms:
 q=t.encode();st=0
 while True:
  o=b.find(q,st)
  if o<0:break
  if 228000<=o<=278000:
   lo=max(0,o-90);hi=min(len(b),o+len(q)+150);ctx=b[lo:hi].decode('utf-8','ignore');ctx=''.join(c if ord(c)>=32 else '·' for c in ctx)
   rows.append({'term':t,'ro_offset':o,'mem':mem+o,'context':ctx})
  st=o+len(q)
print(json.dumps(rows,ensure_ascii=False,indent=2));(D/'title_runtime_candidates_v39.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('HITS',len(rows))
