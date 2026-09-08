from pathlib import Path
import csv,collections,re
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\switch_pc_v4\safe_matches.tsv')
with p.open('r',encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
def esc(s):return s.encode('unicode_escape').decode('ascii')
for label,pred in [
 ('dq-bracket',lambda s:s.startswith('"【') and not s.startswith('"【"')),
 ('dq-bracket-dq',lambda s:s.startswith('"【"')),
 ('leading-double',lambda s:s.startswith('""')),
 ('leading-other',lambda s:s.startswith('"') and not s.startswith('"【') and not s.startswith('""'))]:
 print('\n###',label)
 n=0
 for r in rows:
  s=r['pc_zh_text']
  if pred(s):
   print(r['scene'],r['sw_code_index'],esc(s[:120]))
   n+=1
   if n>=20:break
 print('shown',n)
