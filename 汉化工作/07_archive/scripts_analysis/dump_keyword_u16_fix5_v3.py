from pathlib import Path
import struct
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_work\script_probe\SCRIPT.PAK_unpacked\_KEYWORD').read_bytes()
for off in range(0,850,2):
    v=struct.unpack_from('<H',b,off)[0]
    if off<120 or v<400:
        try: ch=chr(v) if 32<=v<0xD800 else ''
        except: ch=''
        print(f'{off:04X} {v:5d} {v:04X} {ch!r}')
