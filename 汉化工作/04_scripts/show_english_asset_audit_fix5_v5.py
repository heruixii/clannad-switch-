import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\english_asset_change_audit_fix5.json')
for x in json.loads(p.read_text(encoding='utf-8')):
 print(x['pak'],x['asset'],'SAME' if x['same_orig_fix4'] else 'CHANGED',repr(x['texts']))
