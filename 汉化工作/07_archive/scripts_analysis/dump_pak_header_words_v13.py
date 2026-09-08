from pathlib import Path
import struct
for name in ['PARTS.PAK','PARTS2.PAK','SYSCG.PAK','SYSCG2.PAK']:
 p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\ui_work')/name;b=p.read_bytes();print('\n###',name,'len',len(b))
 print('9I',struct.unpack_from('<9I',b,0))
 for off in range(0,192,16):
  vals=struct.unpack_from('<4I',b,off); print(f'{off:04x}',*[f'{v:08x}' for v in vals])
