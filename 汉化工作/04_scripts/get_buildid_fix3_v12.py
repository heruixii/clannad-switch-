from pathlib import Path
import hashlib
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main')
b=p.read_bytes();print('magic',b[:4]);print('buildid',b[0x40:0x60].hex().upper());print('sha',hashlib.sha256(b).hexdigest().upper(),'size',len(b))
