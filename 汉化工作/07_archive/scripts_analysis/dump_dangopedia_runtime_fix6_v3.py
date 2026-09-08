from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
start,end=0x15D000,0x161500
for x in md.disasm(tb[start:end],start):
 if x.mnemonic=='.byte': continue
 print(f'{x.address:08X}: {x.mnemonic:8s} {x.op_str}')
