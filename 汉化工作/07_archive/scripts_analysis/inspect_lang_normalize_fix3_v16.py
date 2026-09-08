from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for a,z,n in [(0xd0d0,0xd2c0,'lang normalize'),(0x1427a0,0x1428a0,'lang init')]:
 print('\n###',n)
 for x in md.disasm(b[a:z],a): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
