from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for lo,hi,name in [(0x178c80,0x179380,'title/config bridge'),(0x17a680,0x17a840,'title later'),(0x177d80,0x1783a0,'config object refs')]:
 print('\n###',name)
 for x in md.disasm(b[lo:hi],lo): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
