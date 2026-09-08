from pathlib import Path
import struct,binascii
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin');b=p.read_bytes();print('size',len(b));print(binascii.hexlify(b[:256]).decode())
for off in range(0,0x80,4):print(f'{off:04x}',hex(struct.unpack_from('<I',b,off)[0]))
