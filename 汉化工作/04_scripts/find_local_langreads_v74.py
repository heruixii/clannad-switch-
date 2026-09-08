from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
def dump_range(lo,hi,name):
 print('\n##',name)
 for i,x in enumerate(ins):
  if not(lo<=x.address<hi):continue
  # look for adrp *247000 + ldr ptr + ldrsw [ptr,#0x8c]
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x247000:
   r=x.operands[0].reg
   for j in range(i+1,min(i+10,len(ins))):
    y=ins[j]
    if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r:
     dest=y.operands[0].reg;slot=0x247000+y.operands[1].mem.disp
     for k in range(j+1,min(j+12,len(ins))):
      z=ins[k]
      if z.mnemonic in ('ldrsw','ldr') and len(z.operands)>1 and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==dest and z.operands[1].mem.disp==0x8c:
       print('LANGREAD',hex(x.address),'slot',hex(slot),'load',hex(z.address))
       for q in ins[max(0,i-8):min(len(ins),k+18)]: print(f'{q.address:08X}: {q.mnemonic:<8} {q.op_str}')
       break
     break
dump_range(0x178000,0x180000,'TITLE region')
dump_range(0x150000,0x156000,'CONFIG region')
