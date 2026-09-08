from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
terms=['Master Volume','Text Speed','Cursor Control','Soft Filter','Color Adjustment','Blue Level','Green Level','Red Level','Font','Sound source','System sounds','Rumble feature','Quick Load','Voice output','Sample Voice','Defaults']
for t in terms:
 o=rb.find(t.encode());
 if o<0:continue
 addr=RB+o; pg=addr&~0xfff; lo=addr&0xfff; hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+5,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     hits.append((x.address,y.address,md.reg_name(r)));break
 print('\n###',t,hex(addr),'hits',len(hits))
 for h in hits:print(*(hex(a) if isinstance(a,int) else a for a in h))
