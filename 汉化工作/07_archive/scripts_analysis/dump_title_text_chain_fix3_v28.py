from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for lo,hi,name in [(0x22980,0x22b40,'229f0'),(0x66180,0x66300,'66220'),(0x657c0,0x65960,'65890')]:
 print('\n###',name)
 for x in md.disasm(b[lo:hi],lo): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
