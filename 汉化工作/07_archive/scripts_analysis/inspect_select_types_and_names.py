from pathlib import Path
import json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
ops=collections.Counter();talk=[];sel=[]
for fp in sorted((ROOT/'03_text/switch_export/script_json').glob('SEEN*.json')):
 d=json.loads(fp.read_text(encoding='utf-8-sig'))
 for ci,c in enumerate(d['codes']):
  ops[c.get('opcode')]+=1
  if c.get('opcode')=='TALKNAME_SET' and len(talk)<20:talk.append((fp.stem,ci,c))
  if c.get('opcode')=='SELECT' and len(sel)<3:sel.append((fp.stem,ci,c))
print('string-ish counts', {k:v for k,v in ops.items() if k in ('MESSAGE','SELECT','TALKNAME_SET','VARSTR','STR','TEXT')})
for sc,ci,c in sel:
 print('SELECT',sc,ci,'info',c.get('info'),'nparams',len(c.get('paramDatas',[])),'types-tail',[(x['type'],x['value']) for x in c['paramDatas'][:8]],'...',[(x['type'],x['value']) for x in c['paramDatas'][-10:]])
for sc,ci,c in talk:
 print('TALK',sc,ci,c)
