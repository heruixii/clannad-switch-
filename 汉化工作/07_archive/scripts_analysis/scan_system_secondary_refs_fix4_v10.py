from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
G=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def findall(addr):
 pg=addr&~0xfff;lo=addr&0xfff;res=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     res.append((x.address,y.address));break
 return res
for g in G:
 old=g['en_addr'];hits=findall(old);known=(g['adrp_off'],g['add_off']);extra=[h for h in hits if h!=known]
 if extra:print(repr(g['en']),'old',hex(old),'known',tuple(hex(x) for x in known),'extra',[(hex(a),hex(b)) for a,b in extra])
