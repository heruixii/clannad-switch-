from pathlib import Path
from capstone import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for start,end,name in [(0x2980,0x2b10,'BACK_CLOSE'),(0x2f70,0x3090,'NEXT'),(0x1c30,0x1d00,'YESNO')]:
 print('\n###',name)
 for x in md.disasm(tb[start:end],start):print(f'{x.address:08X}: {x.mnemonic:8s} {x.op_str}')
