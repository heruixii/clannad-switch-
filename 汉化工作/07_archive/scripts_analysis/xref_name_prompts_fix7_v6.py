from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
for a,name in [(0x1e4ca3,'EN reset'),(0x1e5918,'EN change'),(0x1e30e6,'JP reset'),(0x1e0e4c,'JP change')]:
 pg=a&~0xfff;lo=a&0xfff;hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   reg=x.operands[0].reg
   for j in range(i+1,min(i+8,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==reg and y.operands[1].reg==reg and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     hits.append((x.address,y.address));break
 print(name,hex(a),[(hex(x),hex(y)) for x,y in hits])
 for x,y in hits:
  print(' context')
  for z in ins[max(0,next(i for i,q in enumerate(ins) if q.address==x)-8):][:24]:
   print(hex(z.address),z.mnemonic,z.op_str)
