from pathlib import Path
import json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
p=ROOT/'03_text/switch_export/script_json/SEEN0414.json'
o=json.loads(p.read_text(encoding='utf-8-sig'))
print(type(o), (list(o)[:20] if isinstance(o,dict) else len(o)))
# find command list
if isinstance(o,dict):
 for k,v in o.items():
  if isinstance(v,list) and v and isinstance(v[0],dict): print('LIST',k,len(v),list(v[0])[:20])
# recursive collect dicts with opcode
cmd=[]
def walk(x):
 if isinstance(x,dict):
  if 'opcode' in x:cmd.append(x)
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(o)
print('opcodes',collections.Counter(c.get('opcode') for c in cmd).most_common(30))
for c in [x for x in cmd if x.get('opcode') in ('MESSAGE','SELECT','TALKNAME_SET')][:30]:
 print(json.dumps(c,ensure_ascii=False)[:3000])
