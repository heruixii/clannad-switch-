from pathlib import Path
import csv,re,collections,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\switch_pc_v4\safe_matches.tsv')
with p.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
patterns=collections.Counter(); examples=collections.defaultdict(list); quoteish=[]
for r in rows:
 s=r['pc_zh_text']
 if s.startswith('"【"'):
  k='dq-bracket-dq'
 elif s.startswith('"【'):
  k='dq-bracket'
 elif s.startswith('【'):
  k='clean-bracket'
 elif s.startswith('"'):
  k='leading-dq'
 else:k='plain'
 patterns[k]+=1
 if len(examples[k])<8:examples[k].append(repr(s))
 if '"【' in s or '】"' in s: quoteish.append(s)
print('rows',len(rows));print('patterns',dict(patterns))
for k,v in examples.items():
 print('\n',k)
 for x in v:print(x)
print('quoteish',len(quoteish))
# speaker raw forms top
sp=collections.Counter()
for r in rows:
 s=r['pc_zh_text']
 m=re.match(r'^(?:")?【(.*?)(?:】"|】)',s)
 if m:sp[m.group(1)]+=1
print('top speaker raw')
for k,n in sp.most_common(50):print(n,repr(k))
