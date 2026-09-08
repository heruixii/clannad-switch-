from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
needle=b'_scr_label\0';o=rb.find(needle);a=RB+o;print('STRING',hex(a))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
page=a&~0xfff;off=a&0xfff
for i,x in enumerate(ins):
 if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==page:
  r=x.operands[0].reg
  for j in range(i+1,min(i+5,len(ins))):
   y=ins[j]
   if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==off:
    print('XREF',hex(x.address))
    for z in ins[max(0,i-70):min(len(ins),i+100)]:print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
