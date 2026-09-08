from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
# Find stores to [global language object + 0x8c]. Pattern: adrp/ldr GOT ptr, then str w?, [x?,#0x8c]
for i,x in enumerate(ins):
 if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x247000:
  r=x.operands[0].reg
  for j in range(i+1,min(i+4,len(ins))):
   y=ins[j]
   if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==0xaa8:
    obj=y.operands[0].reg
    for k in range(j+1,min(j+30,len(ins))):
     z=ins[k]
     if z.mnemonic in ('str','stur') and len(z.operands)>1 and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==obj and z.operands[1].mem.disp==0x8c:
      print('\nWRITE',hex(z.address),z.mnemonic,z.op_str,'anchor',hex(x.address))
      for q in ins[max(0,i-12):min(len(ins),k+20)]:print(f'{q.address:08X}: {q.mnemonic:<8} {q.op_str}')
      break
    break
