from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
print('ORIGINAL')
for x in md.disasm(b[0x142838:0x142870],0x142838): print(hex(x.address),x.mnemonic,x.op_str,b[x.address:x.address+4].hex())
patches={
 0x14284c:0x3200c3e8, # mov w8,#0x1010101
 0x142850:0x52800069, # mov w9,#3
 0x142854:0xB9000000 | ((0x9c//4)<<10) | (19<<5) | 8, # str w8,[x19,#0x9c]
}
print('PATCHES')
for a,w in patches.items():
 bb=w.to_bytes(4,'little'); xs=list(md.disasm(bb,a));print(hex(a),hex(w),bb.hex(),[(x.mnemonic,x.op_str) for x in xs])
