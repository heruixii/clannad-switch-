from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0));
for disp in [0x8c,0x308,0x318]:
 print('\n## FIELD',hex(disp))
 hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x247000:
   r=x.operands[0].reg
   for j in range(i+1,min(i+4,len(ins))):
    y=ins[j]
    if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==0xaa8:
     obj=y.operands[0].reg
     for k in range(j+1,min(j+16,len(ins))):
      z=ins[k]
      if z.mnemonic in ('ldr','ldrsw','str','stur') and len(z.operands)>1 and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==obj and z.operands[1].mem.disp==disp:
       hits.append((x.address,z.address,z.mnemonic,z.op_str));break
     break
 print('COUNT',len(hits))
 for h in hits[:260]:print(hex(h[0]),hex(h[1]),h[2],h[3])
