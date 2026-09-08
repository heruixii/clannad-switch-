from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
terms=['Master Volume','Text Speed','Languages','Language','Cursor Control','Color of Read Text','Soft Filter','Color Adjustment','Blue Level','Sound source','System sounds','Voice output','Rumble feature','Auto-Sleep','Quick Load','Sample Voice','Play Voice','Defaults','Basic operation']
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));
for t in terms:
 offs=[];q=t.encode()+b'\0';st=0
 while 1:
  o=rb.find(q,st)
  if o<0:break
  offs.append(RB+o);st=o+1
 for a in offs:
  hits=[];page=a&~0xfff;off=a&0xfff
  for i,x in enumerate(ins):
   if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==page:
    r=x.operands[0].reg
    for j in range(i+1,min(i+5,len(ins))):
     y=ins[j]
     if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==off:
      hits.append((x.address,y.address,md.reg_name(r)));break
  print(t,hex(a),'refs',[(hex(x),hex(y),r) for x,y,r in hits])
