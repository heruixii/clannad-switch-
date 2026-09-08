from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for a,z,n in [(0x17b6d0,0x17bda0,'title_drawish'),(0x70d80,0x71dd0,'text_helpers'),(0x77000,0x77200,'list_measure')]:
 print('\n###',n)
 for x in md.disasm(b[a:z],a):print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
