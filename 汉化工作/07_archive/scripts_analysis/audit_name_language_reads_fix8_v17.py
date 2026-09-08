from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
for lo,hi,name in [(0x168f00,0x16ab80,'NameEdit all'),(0xf8600,0xf89e0,'voice/default restore')]:
 print('\n###',name)
 for x in md.disasm(tb[lo:hi],lo):
  if '#0x8c' in x.op_str.lower() or '#0x34c' in x.op_str.lower() or any(k in x.op_str.lower() for k in ['#0x2b98','#0x2bba','#0x2bdc','#0x2bfe','#0x932','#0x954','#0x976','#0x998']):
   print(f'{x.address:08X} {x.mnemonic:<8} {x.op_str}')
