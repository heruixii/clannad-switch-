import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\ui_lang_pointer_groups_v51.json')
g=json.loads(p.read_text(encoding='utf-8'))
print('TOTAL',len(g),'ADDR_MIN',hex(min(x['adrp_off'] for x in g)),'MAX',hex(max(x['adrp_off'] for x in g)))
for x in g:
 if x['adrp_off']>=0x100000 or x['en'] in ['Defaults','Sample Voice','Basic operation','Languages','Play Voice','Game Start'] or 'Text' in x['en']:
  print(hex(x['adrp_off']),hex(x['add_off']),repr(x['en']),'->',repr(x['zh']),hex(x['en_addr']),hex(x['zh_addr']))
