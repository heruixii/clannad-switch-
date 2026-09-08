from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
ins=list(md.disasm(b[0x1000:0x3100],0x1000))
for i,x in enumerate(ins):
 if x.address<=0x29a0 and x.mnemonic=='ret': print('RET',hex(x.address))
print('--- around last ret ---')
last=max(i for i,x in enumerate(ins) if x.address<0x29a0 and x.mnemonic=='ret')
for x in ins[last:last+120]: print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
