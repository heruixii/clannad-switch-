from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
# find xrefs to strings likely tied to keyword UI
strings=['Dangopedia Keyword','Keyword','_KEYWORD']
for s in strings:
 o=rb.find(s.encode()+b'\0');print('\n##',s,hex(RB+o) if o>=0 else None)
 if o<0:continue
 a=RB+o;pg=a&~0xfff;lo=a&0xfff
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     print('xref',hex(x.address),hex(y.address))
# dump around candidate onDraw symbol string references in nearby code based on c++ symbol names not directly callable
for start,end in [(0x160000,0x165000),(0x168000,0x16d000),(0x170000,0x175000)]:
 print('\nRANGE',hex(start),hex(end))
 for x in ins:
  if start<=x.address<end:
   if x.mnemonic in ('mov','movz','movk','fmov') and any(op.type==ARM64_OP_IMM for op in x.operands):
    vals=[op.imm for op in x.operands if op.type==ARM64_OP_IMM]
    if any(v in (16,18,20,22,24,26,28,30,32,34,36,40,48,52,56,60,64,68,72,80,96,100,120,128,140,160,168,180,192,200,216,224,240,256,280,300,320,336,360,384,400,448,480,512,560,600,640,672,720,768,800,840,960) for v in vals):
     print(hex(x.address),x.mnemonic,x.op_str)
