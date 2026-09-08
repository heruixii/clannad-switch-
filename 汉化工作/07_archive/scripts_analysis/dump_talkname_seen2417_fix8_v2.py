from pathlib import Path
import json
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_export\script_json\SEEN2417.json')
d=json.loads(P.read_text(encoding='utf-8-sig'))
codes=d['codes']
idxs=[i for i,c in enumerate(codes) if c.get('opcode')=='TALKNAME_SET']
print('count',len(idxs),'idxs',idxs[:50])
for i in idxs:
 print('\nINDEX',i)
 for j in range(max(0,i-5),min(len(codes),i+8)):
  c=codes[j]
  print(j,c.get('opcode'),json.dumps(c,ensure_ascii=False)[:2500])
