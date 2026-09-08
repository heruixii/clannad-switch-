from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
ins=list(md.disasm(tb[0x1800:0x3070],0x1800))
for i,x in enumerate(ins):
 if x.address>=0x30014:break
 if x.mnemonic in ('adrp','mov','add','ldr') and x.operands and x.operands[0].type==ARM64_OP_REG and md.reg_name(x.operands[0].reg) in ('x19','x20'):
  ann=''
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM:
   r=x.operands[0].reg;page=x.operands[1].imm
   for j in range(i+1,min(i+5,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
     a=page+y.operands[2].imm
     if RB<=a<RB+len(rb):
      o=a-RB;z=rb.find(b'\0',o,min(len(rb),o+120));
      try:s=rb[o:z].decode('utf-8')
      except:s=''
      ann=f' -> {hex(a)} {s!r}'
     break
  print(f'{x.address:08X}: {x.mnemonic:8s} {x.op_str}{ann}')
