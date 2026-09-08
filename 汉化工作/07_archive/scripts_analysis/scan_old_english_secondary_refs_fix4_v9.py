from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,ast,re,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
rep=json.loads((R/'05_build/fix3_exefs/config_chs_v1_report.json').read_text(encoding='utf-8')); moved={s:v for s,v in rep['placements'].items() if v['moved']}
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
for s,v in moved.items():
 a=int(v['old'],16);pg=a&~0xfff;lo=a&0xfff;text=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     text.append((x.address,y.address));break
 # qword refs in rodata/data
 pat=struct.pack('<Q',a);qrefs=[]
 for nm,b,base in [('rodata',rb,RB),('data',db,DB)]:
  st=0
  while True:
   o=b.find(pat,st)
   if o<0:break
   qrefs.append((nm,base+o));st=o+1
 known=set()
 # config builder refs are not in report, but patched addresses can be inferred later; just flag outside config func
 outside=[x for x in text if not (0x14F000<=x[0]<0x15C000)]
 if outside or qrefs or len(text)>1:
  print('\n',repr(s),'old',hex(a),'all_text',[(hex(x),hex(y)) for x,y in text],'outside',[(hex(x),hex(y)) for x,y in outside],'qrefs',[(n,hex(a)) for n,a in qrefs])
