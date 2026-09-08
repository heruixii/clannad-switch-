from pathlib import Path
from capstone import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
for lo,hi,name in [(0xdc600,0xdcb80,'_TALKNAME loader'),(0x170000,0x170900,'NameEdit')]:
 print('\n###',name,hex(lo),hex(hi))
 for x in md.disasm(tb[lo:hi],lo):
  print(f'{x.address:08X}  {x.mnemonic:<8} {x.op_str}')
