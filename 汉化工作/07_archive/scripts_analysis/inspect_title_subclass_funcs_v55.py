from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for c in [0x179150,0x17bda0,0x17bdb0,0x17be60,0x17ea80,0x14260,0x62420,0x234910 if False else 0]:
 if not c:continue
 a=max(0,c-0x60);z=min(len(b),c+0x220);print('\n###',hex(c))
 for x in md.disasm(b[a:z],a):print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
