from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True
cnt=0;adrp=0
for i,x in enumerate(md.disasm(b,0)):
 if i<80: print(hex(x.address),x.mnemonic,x.op_str,[ (o.type, o.reg if o.type==ARM64_OP_REG else o.imm if o.type==ARM64_OP_IMM else None) for o in x.operands])
 if x.mnemonic=='adrp':
  adrp+=1
  if adrp<=20:print('ADRP',hex(x.address),x.op_str,[(o.type,o.reg if o.type==ARM64_OP_REG else o.imm) for o in x.operands])
 cnt+=1
print('ins',cnt,'adrp',adrp)
