import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\othcg_build_report.json')
d=json.loads(p.read_text(encoding='utf-8'))
print('manual_text',d.get('manual_text'))
print('pc_static count',len(d.get('pc_static',[])))
for x in d.get('pc_static',[]):print(x)
