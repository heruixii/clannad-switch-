from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
targets=[0x1de3d3,0x1e459b,0x1e36e5,0x1dd99a]
for tar in targets:
 print('\nTARGET',hex(tar));hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM: continue
  page=x.operands[1].imm;r=x.operands[0].reg
  if page != (tar & ~0xfff): continue
  for j in range(i+1,min(i+6,len(ins))):
   y=ins[j]
   if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[1].type==ARM64_OP_REG and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
    if page+y.operands[2].imm==tar:
     hits.append((i,j));break
 for i,j in hits:
  print('HIT',hex(ins[i].address))
  for z in ins[max(0,i-45):min(len(ins),j+75)]: print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
 print('COUNT',len(hits))
