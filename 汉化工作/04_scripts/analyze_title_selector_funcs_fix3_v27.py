from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));idx={x.address:i for i,x in enumerate(ins)}
funcs=[0x179270,0x17a2b0,0x17a620,0x17a710,0x17ba20,0x17bda0]
def cstr(a):
 if not(RB<=a<RB+len(rb)):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+300))
 if e<0:return None
 try:s=rb[o:e].decode('utf-8')
 except:return None
 if not s:return None
 return s
for st in funcs:
 i=idx[st];end=min(len(ins),i+3000)
 for j in range(i+1,end):
  if ins[j].mnemonic=='ret':end=j+1;break
 strings=[];calls=[]
 for j in range(i,end):
  x=ins[j]
  if x.mnemonic=='bl' and x.operands and x.operands[0].type==ARM64_OP_IMM:calls.append(x.operands[0].imm)
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM:
   r=x.operands[0].reg;pg=x.operands[1].imm
   for k in range(j+1,min(end,j+5)):
    y=ins[k]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
     s=cstr(pg+y.operands[2].imm)
     if s and s not in strings:strings.append(s)
     break
 print('\nFUNC',hex(st),'END',hex(ins[end-1].address),'INS',end-i)
 print('STRINGS');[print(' ',repr(s)) for s in strings]
 from collections import Counter
 cc=Counter(calls);print('CALLS',[(hex(a),n) for a,n in cc.most_common(30)])
