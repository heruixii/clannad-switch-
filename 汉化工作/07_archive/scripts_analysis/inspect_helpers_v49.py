from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for a,z in [(0x1a1ef0,0x1a1fa0),(0x29a0-0x120,0x29a0)]:
 print('\n###',hex(a),hex(z))
 for x in md.disasm(b[a:z],a):print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
