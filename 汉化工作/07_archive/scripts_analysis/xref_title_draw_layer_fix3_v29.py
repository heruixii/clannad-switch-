from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
for target in [0x17ba20,0x17b710,0x17b6d0,0x17bd9c,0x71ca0]:
 print('\nTARGET',hex(target))
 for i,x in enumerate(ins):
  if x.mnemonic in ('bl','b') and len(x.operands)>0 and x.operands[0].type==ARM64_OP_IMM and x.operands[0].imm==target:
   print('REF',hex(x.address),x.mnemonic,x.op_str)
   for z in ins[max(0,i-8):min(len(ins),i+12)]:print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
