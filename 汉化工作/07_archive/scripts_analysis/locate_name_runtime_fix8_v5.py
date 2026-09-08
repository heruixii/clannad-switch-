from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
terms=[b'_TALKNAME',b'task::Name',b'NameWin',b'Name',b'name',b'STRCMP']
def xrefs(addr):
 pg=addr&~0xfff;lo=addr&0xfff;res=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     res.append((x.address,y.address));break
 return res
for t in terms:
 print('\n##',t)
 st=0;n=0
 while True:
  o=rb.find(t,st)
  if o<0:break
  # only nul-boundary-ish strings
  a=RB+o;z=rb.find(b'\0',o);s=rb[o:z if z>=0 else o+100]
  if len(s)<160:
   rr=xrefs(a)
   if rr:
    print(hex(a),repr(s),[(hex(x),hex(y)) for x,y in rr]);n+=1
  st=o+1
 print('xref_strings',n)
