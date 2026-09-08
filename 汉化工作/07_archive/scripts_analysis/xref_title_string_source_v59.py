from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
# find adrp to 0x249000 then ldr using +0x1b0 nearby
hits=[]
for i,x in enumerate(ins):
 if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x249000:
  r=x.operands[0].reg
  for j in range(i+1,min(i+5,len(ins))):
   y=ins[j]
   if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==0x1b0:
    hits.append((i,j))
for i,j in hits:
 print('\n### hit',hex(ins[i].address))
 for z in ins[max(0,i-60):min(len(ins),j+100)]:print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
print('HITS',len(hits))
