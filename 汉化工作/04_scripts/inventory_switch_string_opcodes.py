from pathlib import Path
import json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=ROOT/'03_text/switch_export/script_json'
ops=collections.Counter();examples=collections.defaultdict(list)
for fp in sorted(SRC.glob('SEEN*.json')):
 d=json.loads(fp.read_text(encoding='utf-8-sig'))
 for i,c in enumerate(d.get('codes',[])):
  op=c.get('opcode','');ops[op]+=1
  if op in ('SELECT','TALKNAME_SET','MESSAGE') and len(examples[op])<8:examples[op].append((fp.stem,i,c))
print('SELECT',ops['SELECT'],'TALKNAME_SET',ops['TALKNAME_SET'],'MESSAGE',ops['MESSAGE'])
for op in ('SELECT','TALKNAME_SET'):
 print('\n###',op)
 for sc,i,c in examples[op]:
  print(sc,i,json.dumps(c,ensure_ascii=False)[:4000])
