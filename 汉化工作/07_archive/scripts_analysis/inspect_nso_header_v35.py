from pathlib import Path
import struct,binascii
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');b=p.read_bytes()
print('magic',b[:4], 'size',len(b));print(binascii.hexlify(b[:0x100]).decode())
for off in range(0,0x80,4): print(f'{off:02X}',struct.unpack_from('<I',b,off)[0],hex(struct.unpack_from('<I',b,off)[0]))
