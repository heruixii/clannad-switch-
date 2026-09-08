from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));idx={x.address:i for i,x in enumerate(ins)}
def cstr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+500))
 if e<0:return None
 try:return rb[o:e].decode('utf-8')
 except:return None
for center in [0x1523fc,0x152c68,0x154104,0x154400,0x154a8c,0x1550cc,0x155254,0x1552c0,0x1553b0,0x155fa8,0x156030,0x156538]:
 i=idx[center];print('\n###',hex(center))
 for j in range(max(0,i-24),min(len(ins),i+45)):
  x=ins[j];ann=''
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM:
   r=x.operands[0].reg;pg=x.operands[1].imm
   for k in range(j+1,min(len(ins),j+5)):
    y=ins[k]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
     s=cstr(pg+y.operands[2].imm)
     if s:ann=' ; '+repr(s[:120])
     break
  print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}{ann}')
