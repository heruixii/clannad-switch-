from pathlib import Path
import json,re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');b=(D/'rodata.bin').read_bytes();B=0x1A3000
terms=['Game Start','New Game','Load','After Story','AfterStory','CG Mode','CG MODE','Music Mode','MUSIC MODE','Config','Configuration','Settings','Name','Dangopedia','Manual','START','LOAD','CONFIG','NAME','MANUAL','AFTER STORY']
rows=[]
for t in terms:
 q=t.encode();st=0
 while 1:
  o=b.find(q,st)
  if o<0:break
  pre=b[o-1] if o else 0;post=b[o+len(q)] if o+len(q)<len(b) else 0
  if pre==0 and post==0:
   rows.append({'term':t,'addr':B+o,'ro':o})
  st=o+1
print(json.dumps(rows,ensure_ascii=False,indent=2))
# For each exact English string, print nearby NUL strings decoded utf8 +/- 400 bytes
for r in rows:
 o=r['ro'];lo=max(0,o-400);hi=min(len(b),o+400);chunk=b[lo:hi];parts=[];cur=lo
 for seg in chunk.split(b'\0'):
  if seg:
   try:s=seg.decode('utf-8')
   except:s=''
   if s and all(ord(c)>=32 for c in s):parts.append(s[:100])
  cur+=len(seg)+1
 print('\n###',r['term'],hex(r['addr']));print(parts[:100])
(D/'exact_title_strings_v54.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
