from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for x in md.disasm(b[0x178c00:0x178f80],0x178c00): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
