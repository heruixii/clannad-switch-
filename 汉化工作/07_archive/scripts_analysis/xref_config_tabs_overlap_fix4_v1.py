from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
terms=['Configuration','Basic','Button1','Button2','Touch','Text1','Text2','Sound','Voice','Screen','Button 1','Button 2']
for t in terms:
 print('\n###',t)
 st=0
 while True:
  o=rb.find(t.encode(),st)
  if o<0:break
  # exact C-string boundary preferred
  prev=rb[o-1] if o else 0; end=o+len(t); nxt=rb[end] if end<len(rb) else 0
  a=RB+o; print('STR',hex(a),'boundary',prev,nxt)
  pg=a&~0xfff;lo=a&0xfff;hits=[]
  for i,x in enumerate(ins):
   if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
    r=x.operands[0].reg
    for j in range(i+1,min(i+6,len(ins))):
     y=ins[j]
     if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
      hits.append((x.address,y.address));break
  print('HITS',[(hex(a),hex(b)) for a,b in hits[:40]])
  st=o+1
