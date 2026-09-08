import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\ui_lang_pointer_groups_v51.json')
g=json.loads(p.read_text(encoding='utf-8'))
print('COUNT',len(g))
for i,x in enumerate(g):
 print(f"{i:03d} code={x['adrp_off']:08X}/{x['add_off']:08X} EN={x['en']!r} -> ZH={x['zh']!r}")
