from pathlib import Path
from capstone import *
from capstone.arm64 import *
import re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def cstr(a):
 if not(RB<=a<RB+len(rb)):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+3000))
 if e<0:return None
 try:return rb[o:e].decode('utf-8')
 except:return None
def has_cjk(s):return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in s)
refs={}
for i,x in enumerate(ins):
 if not(0x14F000<=x.address<0x15C000):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=cstr(a)
   if s and len(re.findall(r'[A-Za-z]',s))>=2 and not has_cjk(s): refs.setdefault((a,s),[]).append((x.address,y.address))
   break
print('UNIQUE',len(refs))
for n,((a,s),hs) in enumerate(sorted(refs.items(),key=lambda kv:min(x[0] for x in kv[1]))):
 print(f'{n:03d}\t{a:08X}\t{len(s.encode())}\t'+','.join(f'{x:08X}/{y:08X}' for x,y in hs)+f'\t{s!r}')
