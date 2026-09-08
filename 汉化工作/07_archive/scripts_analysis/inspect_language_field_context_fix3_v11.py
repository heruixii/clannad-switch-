from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));addr={x.address:i for i,x in enumerate(ins)}
def cstr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+400))
 if e<0:return None
 try:s=rb[o:e].decode('utf-8')
 except:return None
 return s if s and sum(ch.isprintable() for ch in s)>len(s)*.7 else None
for center,name in [(0x57f14,'318@57f'),(0x59c04,'318@59c'),(0xdfdc4,'318@dfd'),(0x14cb3c,'318@14cb'),(0x167708,'318@1677'),(0x178e1c,'318@title'),(0x121268,'8c@1212'),(0x142798,'8c@1427')]:
 i=min(range(len(ins)),key=lambda k:abs(ins[k].address-center));lo=max(0,i-55);hi=min(len(ins),i+85)
 print('\n###',name,hex(center))
 seen=set()
 for j in range(lo,hi):
  x=ins[j];ann=''
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM:
   r=x.operands[0].reg;pg=x.operands[1].imm
   for k in range(j+1,min(hi,j+5)):
    y=ins[k]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
     s=cstr(pg+y.operands[2].imm)
     if s:ann=' ; '+repr(s[:100])
     break
  print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}{ann}')
