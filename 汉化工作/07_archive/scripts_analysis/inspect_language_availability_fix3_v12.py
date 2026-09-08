from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
# find global language object accesses to offsets 0x9c..0xa4, 0x8c,0x90,0x308,0x318
for target in range(0x9c,0xa5):
 hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x247000:
   r=x.operands[0].reg
   for j in range(i+1,min(i+4,len(ins))):
    y=ins[j]
    if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==0xaa8:
     obj=y.operands[0].reg
     for k in range(j+1,min(j+30,len(ins))):
      z=ins[k]
      if z.mnemonic.startswith(('str','ldr')) and len(z.operands)>1 and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==obj and z.operands[1].mem.disp==target:
       hits.append((z.address,z.mnemonic,z.op_str));break
     break
 if hits:
  print('\nOFF',hex(target),'COUNT',len(hits))
  for h in hits:print(hex(h[0]),h[1],h[2])
