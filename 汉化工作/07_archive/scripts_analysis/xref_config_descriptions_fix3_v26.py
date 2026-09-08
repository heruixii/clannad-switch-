from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
terms=['【Soft Filter】','【Color Adjustment】','【Red Level】','【Green Level】','【Blue Level】','【Contrast】','【Saturation】','Base Wait Time','This function is not available in TV mode.','Picture quality adjustment of the touch screen on the console.']
for term in terms:
 # find strings containing term
 print('\n###',term)
 st=0
 while True:
  o=rb.find(term.encode(),st)
  if o<0:break
  a=RB+o; e=rb.find(b'\0',o); s=rb[o:e].decode('utf-8','replace'); print('STR',hex(a),repr(s[:220]))
  pg=a&~0xfff;off=a&0xfff;hits=[]
  for i,x in enumerate(ins):
   if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
    r=x.operands[0].reg
    for j in range(i+1,min(i+7,len(ins))):
     y=ins[j]
     if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==off:
      hits.append((x.address,y.address,'ADD'));break
     if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==off:
      hits.append((x.address,y.address,'LDR'));break
  print('HITS',[(hex(x),hex(y),k) for x,y,k in hits])
  st=o+1
