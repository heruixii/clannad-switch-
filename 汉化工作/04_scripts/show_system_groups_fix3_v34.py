import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\ui_lang_pointer_groups_v51.json')
g=json.loads(p.read_text(encoding='utf-8'))
for i,x in enumerate(g):print(i,repr(x['en']),'->',repr(x['zh']),hex(x['zh_addr']))
