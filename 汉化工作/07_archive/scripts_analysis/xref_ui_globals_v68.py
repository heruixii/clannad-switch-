from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
for slot in [0x247a18,0x247a20,0x247a28,0x247a30,0x247a38,0x247a40,0x247a48,0x247a50]:
 page=slot&~0xfff;off=slot&0xfff;hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==page:
   r=x.operands[0].reg
   for j in range(i+1,min(i+5,len(ins))):
    y=ins[j]
    if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==off:
     hits.append(i);break
 print('\nSLOT',hex(slot),'hits',len(hits))
 for i in hits:
  print('HIT',hex(ins[i].address))
  for z in ins[max(0,i-18):min(len(ins),i+35)]: print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
