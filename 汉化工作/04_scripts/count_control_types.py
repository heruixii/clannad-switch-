from pathlib import Path
import csv,re,collections
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_extracted\switch_messages.tsv')
pat=re.compile(r'\$\[[^\]]*\]|\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w')
c=collections.Counter();rows=collections.Counter()
with p.open('r',encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  ts=pat.findall(r['jp_text'])
  for t in ts:
   k='ruby' if t.startswith('$[') else ('$w' if t=='$w' else ('$W' if t.startswith('$W') else ('$SU' if t.startswith('$SU') else '$S')));c[k]+=1
  for k in set('ruby' if t.startswith('$[') else ('$w' if t=='$w' else ('$W' if t.startswith('$W') else ('$SU' if t.startswith('$SU') else '$S'))) for t in ts):rows[k]+=1
print('TOKENS',dict(c));print('ROWS',dict(rows))
