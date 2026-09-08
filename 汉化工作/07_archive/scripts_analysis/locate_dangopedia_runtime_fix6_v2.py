from pathlib import Path
from capstone import *
from capstone.arm64 import *
import re,json,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
terms=[b'Dangopedia',b'DANGOPEDIA',b'_KEYWORD',b'CL_DP_',b'cDango',b'Dango']
for term in terms:
 print('\n##',term)
 st=0
 while True:
  o=rb.find(term,st)
  if o<0:break
  # extend null string
  z=rb.find(b'\0',o);print(hex(RB+o),rb[o:z].decode('utf-8','replace')[:240]);st=o+1
# RTTI strings around Dango
for m in re.finditer(rb'N4task[^\0]{0,100}Dango[^\0]*\0',rb):print('RTTI',hex(RB+m.start()),m.group()[:-1].decode('ascii','replace'))
# xrefs to any rodata addr containing CL_DP or _KEYWORD exact string
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def refs(addr):
 pg=addr&~0xfff;lo=addr&0xfff;out=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     out.append((x.address,y.address));break
 return out
for s in [b'_KEYWORD',b'CL_DP_BG',b'CL_DP_ITEMS',b'CL_DP_PT',b'CL_DP_TITLE',b'CL_DP_WINDOW']:
 o=rb.find(s+b'\0')
 if o>=0:print('XREF',s,hex(RB+o),[(hex(a),hex(b)) for a,b in refs(RB+o)])
