from pathlib import Path
from capstone import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
ranges=[(0x5dc80,0x5f080,'name helpers A'),(0x60940,0x60d20,'name helpers B'),(0x169200,0x1693c0,'NameEdit init slots'),(0x16a700,0x16ab00,'NameEdit apply/default'),(0xaeb20,0xb0120,'name helpers C')]
for lo,hi,name in ranges:
 print('\n###',name,hex(lo),hex(hi))
 for x in md.disasm(tb[lo:hi],lo):
  if any(k in x.op_str.lower() for k in ['#0x2b98','#0x2bba','#0x2bdc','#0x2bfe','#0x932','#0x954','#0x976','#0x998','#0x8c']) or x.mnemonic in ('cbz','cbnz','b.eq','b.ne','csel','csinc'):
   print(f'{x.address:08X} {x.mnemonic:<8} {x.op_str}')
